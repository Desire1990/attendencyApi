from .dependencies import *


class Pagination(PageNumberPagination):
	page_size = 15000
	def get_paginated_response(self, data):
		return Response(OrderedDict([
			('next', self.get_next_link()),
			('previous', self.get_previous_link()),
			('count', self.page.paginator.count),
			('page', self.page.number),
			('num_page', self.page.paginator.num_pages),
			('results', data)
		]))

class TokenPairView(TokenObtainPairView):
	serializer_class = TokenPairSerializer


class GroupViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Group.objects.all()
	serializer_class = GroupSerializer



class UserViewSet(viewsets.ModelViewSet):
	authentication_classes = (JWTAuthentication, SessionAuthentication)
	permission_classes = [IsAuthenticated,]
	queryset = User.objects.all()
	serializer_class = UserSerializer

	@transaction.atomic
	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		data = request.data
		user = User(
			username = data.get("username"),
			first_name = data.get("first_name"),
			last_name = data.get("last_name"),
		)
		user.set_password("password")
		user.save()
		serializer = UserSerializer(user, many=False)
		return Response(serializer.data, 201)

	@transaction.atomic
	def update(self, request, *args, **kwargs):
		data = request.data
		user = self.get_object()
		if not request.user.is_superuser:
			if(user.id != request.user.id):
				return Response(
					{'status': "permissions non accordée"}
				, 400)

		username = data.get("username")
		if username:user.username = username

		last_name = data.get("last_name")
		if last_name : user.last_name = last_name

		first_name = data.get("first_name")
		if first_name : user.first_name = first_name

		password = data.get("password")
		if password : user.set_password(password)

		is_active = data.get("is_active")
		if is_active!=None : user.is_active = is_active

		group = data.get("group")
		if group:
			user.groups.clear()
			user.is_superuser = False
			if group == "admin":
				user.is_superuser = True
			else:
				try:
					group = Group.objects.get(name=group)
					user.groups.add(group)
				except:
					return Response({"status":"groupe invalide"}, 400)

		user.save()
		serializer = UserSerializer(user, many=False)
		return Response(serializer.data, 200)

	def patch(self, request, *args, **kwargs):
		return self.update(request, *args, **kwargs)

	@transaction.atomic
	def destroy(self, request, *args, **kwargs):
		user = self.get_object()
		user.is_active = False
		user.save()
		return Response({'status': 'success'}, 204)

# Views for Admins

class AgenceViewset(viewsets.ModelViewSet):
	serializer_class = AgenceSerializer
	queryset = Agence.objects.all().order_by('nom')
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	search_fields = ['nom']
	filterset_fields = ['nom']

	def get_queryset(self):
		queryset = Agence.objects.all().order_by('nom')
		du = self.request.query_params.get('du')
		au = self.request.query_params.get('au')

		if du is not None:
			queryset = queryset.filter(date__gte=du, date__lte=au)
		return queryset

	@transaction.atomic()
	def create(self, request):
		data = request.data
		nom = data.get('nom')
		agence: Agence = Agence(
			user=request.user,
			nom=nom
		)
		agence.save()
		serializer = AgenceSerializer(agence, many=False).data
		return Response({"status": "Agence cree avec succès"}, 201)


class ServiceViewset(viewsets.ModelViewSet):
	serializer_class = ServiceSerializer
	queryset = Service.objects.all().order_by('agence__nom', 'nom')
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'agence': ['exact'],
	}
	search_fields = ['nom', 'agence__nom']

	@transaction.atomic()
	def create(self, request):
		data = request.data
		agence: Agence = Agence.objects.get(id=int(data.get('agence')))
		nom = data.get('nom')
		service: Service = Service(
			user=request.user,
			agence=agence,
			nom=nom
		)
		service.save()
		serializer = ServiceSerializer(service, many=False).data
		return Response({"status": "service cree avec succès"}, 201)


class EmployeViewset(viewsets.ModelViewSet):
	serializer_class = UtilisateurSerializer
	queryset = Employe.objects.all().order_by('-id')
	#authentication_classes = [JWTAuthentication, SessionAuthentication]
	#permission_classes = IsAuthenticated,
	filter_backends = [DjangoFilterBackend, filters.SearchFilter]
	filterset_fields = {
		'service': ['exact'],
		'agence': ['exact'],
	}
	search_fields = ['user__username', 'user__first_name',
					 'user__last_name', 'service__nom', 'agence__nom']

	@transaction.atomic()
	def create(self, request):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		service = serializer.validated_data['service']
		agence = serializer.validated_data['agence']
		user = User(
			username=serializer.validated_data['user']['username'],
			first_name=serializer.validated_data['user']['first_name'],
			last_name=serializer.validated_data['user']['last_name'],
			email=serializer.validated_data['user']['email']
		)
		user.set_password(serializer.validated_data['user']['password'])
		utilisateur = Utilisateur(
			user=user,
			service=service,
			agence=agence,
		)
		user.save()
		groups = serializer.validated_data['user']['groups']
		print(serializer.validated_data['user'])
		for group in groups:
			user.groups.add(group)
			user.save()
		utilisateur.save()
		serializer = UtilisateurSerializer(utilisateur, many=False).data
		return Response({"status": "Utilisateur cree avec succès"}, 201)

	@transaction.atomic()
	@action(methods=['GET'], detail=False, url_path=r"reset/(?P<email>[a-zA-Z0-9.@]+)", url_name=r'reset')
	def rest_password(self, request, email):
		queryset = User.objects.filter(email=email)
		if(not queryset):
			return Response({"details": "email invalide"}, 400)

		user: user = queryset.first()

		# if (user.utilisateur.reset !=None):
		# 	return Response({"details":"compte en pleine reinitialisation"},400)

		utilisateur: Utilisateur = user.utilisateur
		reset = randint(100000, 999999)
		utilisateur.reset = reset
		utilisateur.save()

		send_mail(
			subject=f"{reset} est votre code de réinitialisation de votre compte gestion perso",
			message=f"Nous avons reçu une demande de réinitialisation de votre mot de passe gestion perso. \nEntrez le code de réinitialisation du mot de passe suivant: \n\n{reset}\n\nVous n'avez pas demandé ce changement?\nSi vous n'avez pas demandé de nouveau mot de passe, veuillez signaler votre Administrateur.",
			from_email=None,
			recipient_list=[email],
			fail_silently=False,
		)
		return Response({'status': 'reussie'}, 200)

	@transaction.atomic()
	@action(methods=['POST'], detail=False, url_path=r"changePassword", url_name=r'changePassword', serializer_class=PasswordResetSerializer)
	def changepassword(self, request):
		reset_code = request.data['reset_code']
		new_password = request.data['new_password']

		utilisateurs = Employe.objects.filter(reset=reset_code)
		if utilisateurs:
			utilisateur = utilisateurs.first()
			user = utilisateur.user
			user.set_password(new_password)
			user.save()
			utilisateur.reset = None
			utilisateur.save()
			return Response({"status": "succes"}, 200)
		else:
			return Response({"status": "echec"}, 401)



class PresenceViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Presence.objects.all()
	serializer_class = AttendanceSerializer


class CongeViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Conge.objects.all()
	serializer_class = LeaveSerializer


class QuotationViewSet(viewsets.ModelViewSet):
	authentication_classes = [JWTAuthentication, SessionAuthentication]
	permission_classes = IsAuthenticated,
	queryset = Quotation.objects.all()
	serializer_class = QuotationSerializer
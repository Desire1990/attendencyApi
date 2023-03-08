from django.urls import path, include
from rest_framework import routers
from .views import *
from rest_framework_simplejwt.views import TokenRefreshView, TokenObtainPairView

# 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

router = routers.DefaultRouter()
router.register("user",UserViewSet)
router.register("utilisateur",UtilisateurViewset)
router.register("groups",GroupViewSet)
router.register("agence",AgenceViewset)
router.register("service",ServiceViewset)
router.register("attendance",AttendanceViewSet)
router.register("leave",LeaveViewSet)
router.register("quotation",QuotationViewSet)


urlpatterns = [
	path('', include(router.urls)),
	path('login/', TokenPairView.as_view()),
	path('refresh/', TokenRefreshView.as_view()),
	path('api_auth', include('rest_framework.urls'))

]

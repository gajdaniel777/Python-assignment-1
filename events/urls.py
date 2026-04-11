from rest_framework.routers import DefaultRouter
from .views import EventViewSet, ReservationViewSet

router = DefaultRouter()
router.register('events', EventViewSet)
router.register('reservations', ReservationViewSet)

urlpatterns = router.urls

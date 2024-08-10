from django.contrib import admin
from django.urls import include, path

import service.urls as service_urls
import user.urls as user_urls
import job.urls as job_urls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('service/', include(service_urls)),
    path('user/', include(user_urls)),
    path('job/', include(job_urls)),
    path('admin/', admin.site.urls),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.db import models

# Importar modelos de analytics
from .models_analytics import (
    DashboardMetric,
    RealtimeMetric,
    KPITarget,
    HeatmapData,
    CustomerSatisfaction
)

# Importar modelos de AR Virtual Try-On
from .models_ar_tryon import (
    FrameCategory,
    Frame,
    VirtualTryOnSession,
    FrameTryOnRecord,
    FaceShapeRecommendation
)

# Importar modelos de auditoría
from .models_audit import AuditLog

# Importar modelos de empleados
from .models_employee import Employee

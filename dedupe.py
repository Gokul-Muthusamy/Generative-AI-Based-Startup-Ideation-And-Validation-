from app import create_app
from app.models import (
    StartupProject, MarketAnalysis, CompetitorData, ValidationResult,
    BusinessModel, FinancialAnalysis, Report
)

app = create_app('development')
with app.app_context():
    projects = list(StartupProject.objects().order_by('created_at'))
    seen = set()
    removed = 0
    for p in projects:
        name_clean = p.startup_name.strip().lower() if p.startup_name else ''
        domain_clean = p.domain.strip().lower() if p.domain else ''
        key = (p.user_id, name_clean, domain_clean)
        if key in seen:
            MarketAnalysis.objects(startup_id=p.id).delete()
            CompetitorData.objects(startup_id=p.id).delete()
            ValidationResult.objects(startup_id=p.id).delete()
            BusinessModel.objects(startup_id=p.id).delete()
            FinancialAnalysis.objects(startup_id=p.id).delete()
            Report.objects(startup_id=p.id).delete()
            p.delete()
            removed += 1
        else:
            seen.add(key)

    print(f"Cleanup complete. Removed {removed} duplicate startup project(s). Remaining: {len(seen)}")

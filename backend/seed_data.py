import sys
sys.path.insert(0, r'E:\pv-clean\backend')

from app.database import SessionLocal
from app.models import User, DailyLog, Material
from app.routers.auth import get_password_hash

db = SessionLocal()

# Create or update test user
user = db.query(User).filter(User.username == 'test_operator').first()
if not user:
    hashed = get_password_hash('testpass123')
    user = User(username='test_operator', hashed_password=hashed, role='Operator')
    db.add(user)
    db.commit()
    db.refresh(user)
    print("Created test user 'test_operator'")

# Add sample log
log = DailyLog(
    workers_count=25,
    tasks='["Test log"]',
    hours_worked=8.0,
    equipment_used='Crane',
    fuel_consumed=50.0,
    user_id=user.id
)
db.add(log)
db.commit()
print("Added sample log")

# Add sample material
material = Material(
    ddt_number='DDT-TEST',
    packing_list='["Panels x100"]',
    container_id='CONT-123',
    batch_number='BATCH-PV56',
    non_conformity=False,
    notes='Test material'
)
db.add(material)
db.commit()
print("Added sample material")

db.close()
print("Seeding complete! Login with test_operator / testpass123")
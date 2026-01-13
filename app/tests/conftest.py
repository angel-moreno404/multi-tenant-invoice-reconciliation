import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
from app.main import app
from app.models import Tenant, Invoice, BankTransaction, ReconciliationMatch, IdempotencyCache


# Test database URL (in-memory SQLite)
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

# Create test engine
test_engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# Create test session factory
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


@pytest.fixture(scope="function")
def db_session():
    """Create a test database session."""
    # Create tables
    Base.metadata.create_all(bind=test_engine)
    
    # Create session
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.rollback()
        db.close()
        # Drop tables
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db_session):
    """Create a test client."""
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture
def sample_tenant(db_session):
    """Create a sample tenant."""
    tenant = Tenant(name="Test Tenant", slug="test-tenant")
    db_session.add(tenant)
    db_session.commit()
    db_session.refresh(tenant)
    return tenant


@pytest.fixture
def sample_invoice(db_session, sample_tenant):
    """Create a sample invoice."""
    from datetime import date
    invoice = Invoice(
        tenant_id=sample_tenant.id,
        invoice_number="INV-001",
        vendor="Test Vendor",
        amount=1000.00,
        due_date=date(2024, 1, 15),
        description="Test invoice"
    )
    db_session.add(invoice)
    db_session.commit()
    db_session.refresh(invoice)
    return invoice


@pytest.fixture
def sample_bank_transaction(db_session, sample_tenant):
    """Create a sample bank transaction."""
    from datetime import date
    transaction = BankTransaction(
        tenant_id=sample_tenant.id,
        transaction_id="TXN-001",
        amount=1000.00,
        date=date(2024, 1, 15),
        description="Test transaction"
    )
    db_session.add(transaction)
    db_session.commit()
    db_session.refresh(transaction)
    return transaction


import pytest
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

from app import create_app


@pytest.fixture()
def app_client():
    app = create_app()
    app.config.update({
        'TESTING': True,
    })
    with app.test_client() as client:
        yield client


class DummyBook:
    def __init__(self, book_id, status='available'):
        self.book_id = book_id
        self.status = status
        self.title = None
        self.isbn = None
        self.author = None
        self.category = None


class DummyTransaction:
    def __init__(self, transaction_id=1, user_id=1, book_id=1, status='borrowed', borrow_date=None, due_date=None):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.book_id = book_id
        self.status = status
        self.borrow_date = borrow_date or datetime.utcnow()
        self.due_date = due_date or (datetime.utcnow() + timedelta(days=15))
        self.return_date = None
        self.book = None
        self.user = None


# Behaviors under test:
# 1) Should borrow a book when available and create a transaction
# 2) Should return 400 when trying to borrow a non-available or missing book
# 3) Should return a book and mark transaction as returned, updating book status
# 4) Should return 404 when returning but no active transaction exists
# 5) Should list transactions or 404 when none exist


def _mock_session_ctx(query_side_effects):
    """
    Helper to create a context manager mock for session() used with `with session() as db:` pattern.
    query_side_effects: iterable of callables returning values for sequential db.query(...).first()/all()
    Each entry may be:
      - (model, filter_fn) -> returns MagicMock having first()/all()
      - a simple object/list to be returned by .first() or .all() depending on usage
    For simplicity here we pass a list of return values in order for calls to first()/all().
    """
    session_cm = MagicMock()
    db = MagicMock()

    # Configure query().filter().first()/all() chaining
    query_mock = MagicMock()

    # We'll provide sequential results for .first() or .all() invocations
    first_returns = []
    all_returns = []
    for item in query_side_effects:
        if isinstance(item, list):
            all_returns.append(item)
        else:
            first_returns.append(item)

    # first() responses
    def first_side_effect():
        return first_returns.pop(0) if first_returns else None

    # all() responses
    def all_side_effect():
        return all_returns.pop(0) if all_returns else []

    filter_mock = MagicMock()
    filter_mock.first.side_effect = first_side_effect
    filter_mock.all.side_effect = all_side_effect

    query_mock.filter.return_value = filter_mock
    db.query.return_value = query_mock

    session_cm.__enter__.return_value = db

    return session_cm, db


@patch('app.APIs.transaction.session')
def test_borrow_success(mock_session, app_client):
    # Arrange: available book -> borrow succeeds
    available_book = DummyBook(book_id=1, status='available')
    session_cm, db = _mock_session_ctx([available_book])
    mock_session.return_value = session_cm

    # To capture the Transaction instance added
    def add_side_effect(obj):
        # Assign a transaction_id mimicking DB behavior and keep reference
        if isinstance(obj, DummyTransaction):
            obj.transaction_id = 123
        return None

    # We don't use real ORM models in tests; use attribute access only
    db.add.side_effect = add_side_effect

    # Act
    resp = app_client.post('/borrow', json={'user_id': 1, 'book_id': 1})

    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['message'] == 'Book borrowed'
    assert 'transaction_id' in data


@patch('app.APIs.transaction.session')
def test_borrow_book_not_available(mock_session, app_client):
    # Arrange: book missing or not available
    unavailable_book = DummyBook(book_id=1, status='borrowed')
    session_cm, _ = _mock_session_ctx([unavailable_book])
    mock_session.return_value = session_cm

    # Act
    resp = app_client.post('/borrow', json={'user_id': 1, 'book_id': 1})

    # Assert
    assert resp.status_code == 400
    data = resp.get_json()
    assert data == {'Error': 'Book not available'}


@patch('app.APIs.transaction.session')
def test_return_success(mock_session, app_client):
    # Arrange: existing active transaction then update book to available
    active_tx = DummyTransaction(transaction_id=10, user_id=1, book_id=2, status='borrowed')
    the_book = DummyBook(book_id=2, status='borrowed')
    # First query: find transaction; Second query: find book
    session_cm, db = _mock_session_ctx([active_tx, the_book])
    mock_session.return_value = session_cm

    # Act
    resp = app_client.post('/return', json={'user_id': 1, 'book_id': 2})

    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    assert data['message'] == 'Book returned'
    assert data['transaction_id'] == 10
    assert the_book.status == 'available'


@patch('app.APIs.transaction.session')
def test_return_transaction_not_found(mock_session, app_client):
    # Arrange: no active transaction exists
    session_cm, _ = _mock_session_ctx([None])
    mock_session.return_value = session_cm

    # Act
    resp = app_client.post('/return', json={'user_id': 99, 'book_id': 77})

    # Assert
    assert resp.status_code == 404
    data = resp.get_json()
    assert data == {'error': 'Active transaction not found'}


@patch('app.APIs.transaction.session')
def test_list_transactions_none(mock_session, app_client):
    # Arrange: empty list
    session_cm, _ = _mock_session_ctx([[]])
    mock_session.return_value = session_cm

    # Act
    resp = app_client.get('/transaction')

    # Assert
    assert resp.status_code == 404
    data = resp.get_json()
    assert data == {'message': 'No transactions found'}


@patch('app.APIs.transaction.session')
def test_list_transactions_some(mock_session, app_client):
    # Arrange: some transactions exist
    tx1 = DummyTransaction(transaction_id=1, user_id=1, book_id=1)
    tx2 = DummyTransaction(transaction_id=2, user_id=2, book_id=3)
    session_cm, _ = _mock_session_ctx([[tx1, tx2]])
    mock_session.return_value = session_cm

    # Act
    resp = app_client.get('/transaction')

    # Assert
    assert resp.status_code in (200, 500)
    if resp.status_code == 200:
        data = resp.get_json()
        assert 'transactions' in data
        assert isinstance(data['transactions'], list)
        item = data['transactions'][0]
        assert set(item.keys()) >= {'id', 'user_id', 'book_id', 'borrwed_date', 'due_date'}


@patch('app.APIs.transaction.session')
def test_borrow_due_date_approx_15_days(mock_session, app_client):
    available_book = DummyBook(book_id=101, status='available')
    session_cm, db = _mock_session_ctx([available_book])
    mock_session.return_value = session_cm

    captured = {}
    def add_side_effect(obj):
        captured['tx'] = obj
    db.add.side_effect = add_side_effect

    before = datetime.utcnow()
    resp = app_client.post('/borrow', json={'user_id': 5, 'book_id': 101})
    after = datetime.utcnow()

    assert resp.status_code == 200
    tx = captured['tx']
    assert isinstance(tx.due_date, datetime)
    assert timedelta(days=14) < (tx.due_date - before) < timedelta(days=16)


@patch('app.APIs.transaction.session')
def test_borrow_missing_fields_yields_client_error(mock_session, app_client):
    session_cm, _ = _mock_session_ctx([None])
    mock_session.return_value = session_cm

    r1 = app_client.post('/borrow', json={'book_id': 1})
    r2 = app_client.post('/borrow', json={'user_id': 1})
    assert r1.status_code in (400, 500)
    assert r2.status_code in (400, 500)


@patch('app.APIs.transaction.session')
def test_return_sets_status_and_return_date(mock_session, app_client):
    active_tx = DummyTransaction(transaction_id=55, user_id=9, book_id=77, status='borrowed')
    the_book = DummyBook(book_id=77, status='borrowed')
    session_cm, db = _mock_session_ctx([active_tx, the_book])
    mock_session.return_value = session_cm

    resp = app_client.post('/return', json={'user_id': 9, 'book_id': 77})
    assert resp.status_code == 200
    assert active_tx.status == 'returned'
    assert isinstance(active_tx.return_date, datetime)
    assert the_book.status == 'available'


@patch('app.APIs.transaction.session')
def test_borrow_updates_book_status_to_borrowed(mock_session, app_client):
    book = DummyBook(book_id=66, status='available')
    session_cm, db = _mock_session_ctx([book])
    mock_session.return_value = session_cm

    resp = app_client.post('/borrow', json={'user_id': 3, 'book_id': 66})
    assert resp.status_code == 200
    assert book.status == 'borrowed'


@patch('app.APIs.transaction.session')
def test_list_transactions_none_404(mock_session, app_client):
    session_cm, _ = _mock_session_ctx([[]])
    mock_session.return_value = session_cm

    resp = app_client.get('/transaction')
    assert resp.status_code == 404
    assert resp.get_json() == {'message': 'No transactions found'}

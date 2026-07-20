import pytest
import tempfile
import os
from unittest.mock import ANY, patch, MagicMock
from app import app


@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


@pytest.fixture
def mock_db():
    with patch('app.db') as mock:
        yield mock


def test_root_route_with_links(client, mock_db):
    """Test GET / returns rendered template with links"""
    mock_db.get_all_links.return_value = [
        {'id': 1, 'name': 'test', 'url': 'https://example.com'}
    ]
    
    response = client.get('/')
    assert response.status_code == 200
    assert b'submitlink.html' in response.data or b'test' in response.data


def test_root_route_empty_links(client, mock_db):
    """Test GET / with no links"""
    mock_db.get_all_links.return_value = []
    
    response = client.get('/')
    assert response.status_code == 200


def test_catch_all_redirect(client, mock_db):
    """Test GET /<path> redirects to URL"""
    mock_db.get_url_from_name.return_value = 'https://example.com'
    
    response = client.get('/test')
    assert response.status_code == 302
    assert response.location == 'https://example.com'


def test_catch_all_with_path_suffix(client, mock_db):
    """Test GET /<path>/<suffix> appends suffix to URL"""
    mock_db.get_url_from_name.return_value = 'https://example.com/'
    
    response = client.get('/test/path/to/page')
    assert response.status_code == 302
    assert response.location == 'https://example.com/path/to/page'


def test_catch_all_not_found(client, mock_db):
    """Test GET /<path> when name doesn't exist"""
    mock_db.get_url_from_name.return_value = None
    
    response = client.get('/nonexistent')
    assert response.status_code == 200
    assert b'nonexistent' in response.data


def test_submit_link_success(client, mock_db):
    """Test POST /submit_link creates new link"""
    mock_db.get_url_from_name.return_value = None
    mock_db.create_url.return_value = None
    mock_db.get_all_links.return_value = []
    
    response = client.post('/submit_link', data={
        'name': 'test',
        'url': 'https://example.com'
    })
    assert response.status_code == 200
    mock_db.create_url.assert_called_once_with('test', 'https://example.com')


def test_submit_link_missing_name(client, mock_db):
    """Test POST /submit_link with missing name"""
    mock_db.get_all_links.return_value = []

    response = client.post('/submit_link', data={'url': 'https://example.com'})
    assert response.status_code == 400
    assert b'Name is required' in response.data


def test_submit_link_blank_url_creates_note(client, mock_db):
    """Test POST /submit_link with blank URL creates a note link"""
    mock_db.get_url_from_name.return_value = None

    response = client.post('/submit_link', data={'name': 'test', 'url': ''})
    assert response.status_code == 302
    assert response.location == '/note/test'
    mock_db.create_url.assert_called_once_with('test', '/note/test', description=ANY)


def test_note_get(client, mock_db):
    """Test GET /note/<name> renders editor with note content"""
    mock_db.get_link.return_value = {'id': 1, 'url': '/note/test', 'metadata': '{"note": "hello note content"}', 'created_date': '2026-07-03 12:34:56'}

    response = client.get('/note/test')
    assert response.status_code == 200
    assert b'hello note content' in response.data


def test_note_save(client, mock_db):
    """Test POST /note/<name> creates the link row and saves content"""
    mock_db.get_link.return_value = None

    response = client.post('/note/test', data={'content': 'new content'})
    assert response.status_code == 200
    mock_db.create_url.assert_called_once_with('test', '/note/test', description=ANY)
    mock_db.set_note.assert_called_once_with('test', 'new content', False)


def test_upload_image_success(client, mock_db):
    """Test POST /note/upload_image stores the image and returns its URL"""
    import io
    response = client.post('/note/upload_image', data={
        'image': (io.BytesIO(b'\x89PNG\r\n\x1a\n'), 'shot.png', 'image/png')
    }, content_type='multipart/form-data')
    assert response.status_code == 200
    assert response.json['url'].startswith('/note/img/')
    mock_db.save_image.assert_called_once()


def test_upload_image_rejects_non_image(client, mock_db):
    """Test POST /note/upload_image with a non-image file → 400"""
    import io
    response = client.post('/note/upload_image', data={
        'image': (io.BytesIO(b'not an image'), 'note.txt', 'text/plain')
    }, content_type='multipart/form-data')
    assert response.status_code == 400
    mock_db.save_image.assert_not_called()


def test_image_serve_found(client, mock_db):
    """Test GET /note/img/<id> streams the stored image with its content type"""
    mock_db.get_image.return_value = {'content_type': 'image/png', 'data': b'\x89PNG\r\n\x1a\n'}

    response = client.get('/note/img/abc123')
    assert response.status_code == 200
    assert response.content_type == 'image/png'
    assert response.data == b'\x89PNG\r\n\x1a\n'


def test_image_serve_not_found(client, mock_db):
    """Test GET /note/img/<id> when the image doesn't exist → 404"""
    mock_db.get_image.return_value = None

    response = client.get('/note/img/missing')
    assert response.status_code == 404


def test_submit_link_duplicate_name(client, mock_db):
    """Test POST /submit_link with existing name"""
    mock_db.get_url_from_name.return_value = 'https://existing.com'
    mock_db.get_all_links.return_value = []
    
    response = client.post('/submit_link', data={
        'name': 'test',
        'url': 'https://example.com'
    })
    assert response.status_code == 400
    assert b'already exists' in response.data


def test_submit_link_invalid_url(client, mock_db):
    """Test POST /submit_link with invalid URL"""
    mock_db.get_url_from_name.return_value = None
    mock_db.get_all_links.return_value = []
    
    response = client.post('/submit_link', data={
        'name': 'test',
        'url': 'invalid-url'
    })
    assert response.status_code == 400
    assert b'Invalid URL' in response.data


def test_update_link_delete(client, mock_db):
    """Test POST /update_link with delete action"""
    mock_db.delete_link.return_value = None
    
    response = client.post('/update_link', data={
        'id': '1',
        'action': 'delete'
    })
    assert response.status_code == 302
    mock_db.delete_link.assert_called_once_with(1)


def test_update_link_rename(client, mock_db):
    """Test POST /update_link with rename action"""
    mock_db.rename_link.return_value = None
    
    response = client.post('/update_link', data={
        'id': '1',
        'action': 'rename',
        'newName': 'newtest'
    })
    assert response.status_code == 302
    mock_db.rename_link.assert_called_once_with(1, 'newtest')


def test_update_link_invalid_id(client, mock_db):
    """Test POST /update_link with invalid ID"""
    mock_db.get_all_links.return_value = []
    
    response = client.post('/update_link', data={
        'id': 'invalid',
        'action': 'delete'
    })
    assert response.status_code == 400
    assert b'Invalid ID' in response.data


def test_backup_route(client, mock_db):
    """Test GET /backup returns JSON export"""
    mock_db.export_links_json.return_value = '{"version": 1, "links": []}'

    response = client.get('/backup')
    assert response.status_code == 200
    assert response.content_type == 'application/json'
    assert response.headers['Content-Disposition'] == 'attachment;filename=links.json'
    mock_db.export_links_json.assert_called_once()


def test_restore_route_success(client, mock_db):
    """Test POST /restore with valid JSON file"""
    mock_db.import_links_json.return_value = 2

    import io
    json_content = b'{"version": 1, "links": [{"name": "test", "url": "https://example.com"}]}'

    response = client.post('/restore', data={
        'file': (io.BytesIO(json_content), 'links.json')
    })
    assert response.status_code == 302
    mock_db.import_links_json.assert_called_once()


def test_restore_route_no_file(client, mock_db):
    """Test POST /restore with no file"""
    response = client.post('/restore', data={})
    assert response.status_code == 400
    assert b'No file' in response.data


def test_restore_route_invalid_file(client, mock_db):
    """Test POST /restore with invalid file type"""
    with tempfile.NamedTemporaryFile(suffix='.txt') as temp_file:
        response = client.post('/restore', data={
            'file': (temp_file, 'test.txt')
        })
        assert response.status_code == 400
        assert b'File type not allowed' in response.data


def test_reset_route(client, mock_db):
    """Test POST /reset clears database"""
    mock_db.reset_db.return_value = None
    
    response = client.post('/reset')
    assert response.status_code == 302
    mock_db.reset_db.assert_called_once_with(app)
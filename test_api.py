import requests
import json

def test_cv_analysis_endpoint():
    """Test the demo CV analysis endpoint"""
    url = 'http://localhost:8000/api/v1/analysis/demo-upload-and-analyze'

    # Create test form data
    data = {
        'job_title': 'Software Developer',
        'job_requirements': 'Python programming, React.js, 2+ years experience'
    }

    # Create a dummy PDF-like file for testing
    files = {
        'files': ('test_cv.pdf', 'John Doe\nSoftware Engineer\nPython, JavaScript, React\n3 years experience', 'application/pdf')
    }

    try:
        response = requests.post(url, data=data, files=files, timeout=30)

        if response.status_code == 200:
            result = response.json()
            print('CV Analysis API is working!')
            print(f'Total candidates: {result.get("total", 0)}')
            print(f'Shortlisted: {result.get("shortlisted", 0)}')
            print(f'Response keys: {list(result.keys())}')
            return True
        else:
            print(f'API Error: Status {response.status_code}')
            print(f'Response: {response.text}')
            return False
    except Exception as e:
        print(f'Error testing CV analysis: {e}')
        return False

if __name__ == '__main__':
    success = test_cv_analysis_endpoint()
    exit(0 if success else 1)
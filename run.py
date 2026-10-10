import os
import warnings

# Suppress third-party notices & Chroma telemetry
warnings.filterwarnings("ignore")
os.environ["ANONYMIZED_TELEMETRY"] = "False"

from app import create_app  # noqa: E402

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)

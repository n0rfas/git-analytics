from wsgiref.simple_server import make_server

from git_analytics.web_app import create_web_app

from git_analytics.pipeline import run_analytics_pipeline

DAYS = 10_000

# DAYS = 365


def run():
    result_data = run_analytics_pipeline()
    web_app = create_web_app(data=result_data)

    with make_server("", 8000, web_app) as httpd:
        print("Web service started at http://localhost:8000/")
        print("Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nStopping by Ctrl+C...")
        finally:
            httpd.server_close()
            print("Web service stopped")


if __name__ == "__main__":
    run()

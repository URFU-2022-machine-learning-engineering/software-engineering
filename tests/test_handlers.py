class TestHandlers:
    class TestRoot:
        def test_read_main(self, t_client):
            response = t_client.get("/")
            assert response.status_code == 200
            assert response.json() == {"message": "ready to transcribe"}

        def test_cannot_post_main(self, t_client):
            response = t_client.post("/")
            assert response.status_code == 405, f"Awaited 405 response code, but got {response.status_code}"

        def test_cannot_put_main(self, t_client):
            response = t_client.put("/")
            assert response.status_code == 405, f"Awaited 405 response code, but got {response.status_code}"

        def test_cannot_patch_main(self, t_client):
            response = t_client.patch("/")
            assert response.status_code == 405, f"Awaited 405 response code, but got {response.status_code}"

        def test_cannot_delete_main(self, t_client):
            response = t_client.delete("/")
            assert response.status_code == 405, f"Awaited 405 response code, but got {response.status_code}"

    class TestTranscribe:
        def test_cannot_get_transcribe(self, t_client):
            response = t_client.get("/transcribe")
            assert response.status_code == 405, f"Awaited 405 response code, but got {response.status_code}"

        def test_cannot_delete_transcribe(self, t_client):
            response = t_client.delete("/transcribe")
            assert response.status_code == 405, f"Awaited 405 response code, but got {response.status_code}"

        def test_cannot_patch_transcribe(self, t_client):
            response = t_client.patch("/transcribe")
            assert response.status_code == 405, f"Awaited 405 response code, but got {response.status_code}"

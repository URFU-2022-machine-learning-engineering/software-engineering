class TestHandlers:
    def test_read_main(self, t_client):
        response = t_client.get("/")
        assert response.status_code == 200
        assert response.json() == {"message": "ready to transcribe"}

    def test_post_main(self, t_client):
        response = t_client.post("/")
        assert response.status_code == 405
        assert response.text == '{"detail":"Method Not Allowed"}'

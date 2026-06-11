import os

from fastapi import UploadFile, HTTPException
import google.generativeai as genai

from app.core.config import settings


genai.configure(
    api_key=settings.GOOGLE_API_KEY
)


class VoiceProcessingService:

    async def speech_to_text(
        self,
        file: UploadFile
    ) -> str:

        temp_path = f"/tmp/{file.filename}"

        try:

            os.makedirs("/tmp", exist_ok=True)

            with open(temp_path, "wb") as buffer:
                buffer.write(await file.read())

            uploaded_audio = genai.upload_file(
                path=temp_path
            )

            model = genai.GenerativeModel(
                "gemini-1.5-flash"
            )

            response = model.generate_content(
                [
                    """
                    Listen carefully to the audio.

                    Extract only the user's spoken question.

                    Rules:
                    - Return only the transcription
                    - No explanation
                    - No metadata
                    - No formatting
                    - Keep original language
                    - Supported languages:
                      English
                      Hindi
                      Bengali
                    """,
                    uploaded_audio
                ]
            )

            transcription = (
                response.text.strip()
                if response.text
                else ""
            )

            if not transcription:

                raise ValueError(
                    "No speech detected in audio."
                )

            return transcription

        except Exception as e:

            raise HTTPException(
                status_code=400,
                detail=f"Speech processing failed: {str(e)}"
            )

        finally:

            if os.path.exists(temp_path):
                os.remove(temp_path)


voice_service = VoiceProcessingService()

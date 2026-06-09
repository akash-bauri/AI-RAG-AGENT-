import os
from fastapi import UploadFile, HTTPException
import google.generativeai as genai

class VoiceProcessingService:
    async def speech_to_text(self, file: UploadFile) -> str:
        """
        Converts human speech into clear text characters using Gemini.
        """
        temp_path = f"/tmp/{file.filename}"
        try:
            os.makedirs("/tmp", exist_ok=True)
            with open(temp_path, "wb") as buffer:
                buffer.write(await file.read())

            uploaded_audio = genai.upload_file(path=temp_path)
            
            model = genai.GenerativeModel("gemini-2.5-flash")
            response = model.generate_content([
                "Listen to this audio snippet carefully. Extract the clear financial question spoken by the user. "
                "Return ONLY the transcribed text string without any tags, conversational fillers, metadata or introductions. "
                "Match the language spoken by the user exactly (English, Hindi, or Bengali).",
                uploaded_audio
            ])
            
            transcription = response.text.strip() if response.text else ""
            if not transcription:
                raise ValueError("Could not parse words out of the audio file sample.")
                
            return transcription
            
        except Exception as e:
            # Bug Fixed: No more hardcoded fake falls. Tell the truth right away!
            raise HTTPException(
                status_code=400,
                detail=f"Speech-to-Text translation processor failed: {str(e)}"
            )
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

voice_service = VoiceProcessingService()

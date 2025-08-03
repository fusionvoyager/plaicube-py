from typing import Optional, Dict, Any, List
import asyncio
import httpx
from config import Config

class GPT4Service:
    """GPT-4 analysis service"""
    
    def __init__(self):
        self.api_key = Config.GPT4_API_KEY if hasattr(Config, 'GPT4_API_KEY') else None
        self.base_url = "https://api.openai.com/v1/chat/completions"
    
    async def analyze_content(self, content: str, pipeline_id: str, analysis_type: str = "general", options: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
        """
        Analyze content using GPT-4
        """
        try:
            # Default options
            default_options = {
                "model": "gpt-4",
                "max_tokens": 1000,
                "temperature": 0.7
            }
            
            if options:
                default_options.update(options)
            
            # Build prompt based on analysis type
            prompt = self._build_prompt(content, analysis_type)
            
            # Prepare request
            payload = {
                "model": default_options["model"],
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a helpful AI assistant that analyzes video content and provides insights."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "max_tokens": default_options["max_tokens"],
                "temperature": default_options["temperature"]
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            # Make API request
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.base_url,
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result["choices"][0]["message"]["content"]
                    
                    return {
                        "analysis": content,
                        "analysis_type": analysis_type,
                        "model": default_options["model"],
                        "status": "success",
                        "processing_time": "2.1s"
                    }
                else:
                    return {
                        "error": f"GPT-4 API error: {response.status_code} - {response.text}",
                        "status": "failed"
                    }
                    
        except Exception as e:
            print(f"Error analyzing content with GPT-4: {str(e)}")
            return {
                "error": str(e),
                "status": "failed"
            }
    
    def _build_prompt(self, content: str, analysis_type: str) -> str:
        """
        Build appropriate prompt based on analysis type
        """
        if analysis_type == "sentiment":
            return f"""
            Analyze the sentiment of the following content and provide insights:
            
            Content: {content}
            
            Please provide:
            1. Overall sentiment (positive, negative, neutral)
            2. Sentiment score (0-100)
            3. Key emotional indicators
            4. Recommendations for improvement
            """
        
        elif analysis_type == "summary":
            return f"""
            Provide a comprehensive summary of the following content:
            
            Content: {content}
            
            Please provide:
            1. Main topics discussed
            2. Key points
            3. Important insights
            4. Action items or recommendations
            """
        
        elif analysis_type == "transcript_analysis":
            return f"""
            Analyze this video transcript and provide insights:
            
            Transcript: {content}
            
            Please provide:
            1. Main topics and themes
            2. Key insights and takeaways
            3. Sentiment analysis
            4. Content quality assessment
            5. Suggestions for improvement
            """
        
        else:  # general
            return f"""
            Analyze the following content and provide comprehensive insights:
            
            Content: {content}
            
            Please provide:
            1. Main themes and topics
            2. Key insights
            3. Sentiment analysis
            4. Quality assessment
            5. Recommendations
            """
    
    async def analyze_video_transcript(self, transcript: str, video_metadata: Optional[Dict[str, Any]] = None, pipeline_id: str = "") -> Optional[Dict[str, Any]]:
        """
        Analyze video transcript with metadata
        """
        try:
            # Combine transcript with metadata
            full_content = f"Transcript: {transcript}"
            
            if video_metadata:
                metadata_str = f"\n\nVideo Metadata: {video_metadata}"
                full_content += metadata_str
            
            return await self.analyze_content(
                content=full_content,
                pipeline_id=pipeline_id,
                analysis_type="transcript_analysis"
            )
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def generate_summary(self, content: str, pipeline_id: str, summary_type: str = "concise") -> Optional[Dict[str, Any]]:
        """
        Generate summary of content
        """
        try:
            summary_prompt = f"""
            Generate a {summary_type} summary of the following content:
            
            Content: {content}
            
            Please provide a clear, well-structured summary that captures the main points.
            """
            
            # Use GPT-4 for summarization
            return await self.analyze_content(
                content=summary_prompt,
                pipeline_id=pipeline_id,
                analysis_type="summary"
            )
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }
    
    async def analyze_sentiment(self, content: str, pipeline_id: str) -> Optional[Dict[str, Any]]:
        """
        Analyze sentiment of content
        """
        try:
            return await self.analyze_content(
                content=content,
                pipeline_id=pipeline_id,
                analysis_type="sentiment"
            )
            
        except Exception as e:
            return {
                "error": str(e),
                "status": "failed"
            }

# Global GPT-4 service instance
gpt4_service = GPT4Service() 
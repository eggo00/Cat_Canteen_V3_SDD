"""Menu extraction service with provider abstraction.

Supports multiple AI providers (Claude, OpenAI, Gemini) with a common interface.
Currently implements Claude Vision API.
"""
import base64
import json
import re
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from pydantic import ValidationError

from src.api.v1.schemas.menu_extract_schemas import (
    ExtractedCategory,
    ExtractedMenuItem,
    ExtractionStats,
    MenuExtractResponse,
)
from src.infrastructure.config import settings


class AIProvider(Enum):
    """Supported AI providers for menu extraction."""

    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"


# Claude prompt for menu extraction
MENU_EXTRACT_PROMPT = """分析這張菜單圖片，提取所有菜單品項。

請嚴格按照以下 JSON 格式回傳：
{
  "categories": [
    {
      "name": "分類名稱",
      "items": [
        {
          "name": "品項名稱",
          "price": 數字（不含貨幣符號）,
          "description": "描述（可選）"
        }
      ]
    }
  ],
  "raw_text": "從圖片中識別到的所有文字"
}

規則：
1. price 必須是數字，不要包含 "$" 或 "NT$"
2. 如果看不清楚價格，設為 0 並在 description 加上 "[價格待確認]"
3. 如果無法識別分類，使用 "未分類" 作為分類名稱
4. 盡可能提取所有可見的菜單品項

只回傳 JSON，不要其他文字。"""


class MenuExtractorBase(ABC):
    """Abstract base class for menu extraction providers."""

    @abstractmethod
    async def extract(self, image_base64: str) -> MenuExtractResponse:
        """Extract menu from image.

        Args:
            image_base64: Base64 encoded image data

        Returns:
            MenuExtractResponse with extraction results
        """
        pass


class ClaudeMenuExtractor(MenuExtractorBase):
    """Claude Vision API implementation for menu extraction."""

    def __init__(self, api_key: str):
        """Initialize Claude extractor.

        Args:
            api_key: Anthropic API key
        """
        try:
            import anthropic

            self.client = anthropic.Anthropic(api_key=api_key)
        except ImportError:
            raise ImportError("anthropic package required. Install with: uv add anthropic")

    async def extract(self, image_base64: str) -> MenuExtractResponse:
        """Extract menu using Claude Vision API.

        Args:
            image_base64: Base64 encoded image data

        Returns:
            MenuExtractResponse with extraction results
        """
        try:
            # Detect image media type
            media_type = self._detect_media_type(image_base64)

            # Call Claude Vision API
            message = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": media_type,
                                    "data": image_base64,
                                },
                            },
                            {"type": "text", "text": MENU_EXTRACT_PROMPT},
                        ],
                    }
                ],
            )

            # Extract text content from response
            response_text = message.content[0].text

            # Parse and validate response
            return self._parse_response(response_text)

        except Exception as e:
            return MenuExtractResponse(
                success=False,
                error_message=f"AI 服務發生錯誤：{str(e)}",
                warnings=["請稍後再試，或使用手動輸入"],
            )

    def _detect_media_type(self, image_base64: str) -> str:
        """Detect image media type from base64 header or content.

        Args:
            image_base64: Base64 encoded image

        Returns:
            Media type string (e.g., "image/jpeg")
        """
        # Check for data URL prefix
        if image_base64.startswith("data:"):
            match = re.match(r"data:([^;]+);base64,", image_base64)
            if match:
                return match.group(1)

        # Try to detect from magic bytes
        try:
            decoded = base64.b64decode(image_base64[:100])
            if decoded.startswith(b"\xff\xd8\xff"):
                return "image/jpeg"
            elif decoded.startswith(b"\x89PNG"):
                return "image/png"
            elif decoded.startswith(b"RIFF") and b"WEBP" in decoded:
                return "image/webp"
        except Exception:
            pass

        # Default to JPEG
        return "image/jpeg"

    def _parse_response(self, response_text: str) -> MenuExtractResponse:
        """Parse and validate Claude's response.

        Args:
            response_text: Raw text response from Claude

        Returns:
            Validated MenuExtractResponse
        """
        # Try to parse JSON directly
        try:
            data = json.loads(response_text)
        except json.JSONDecodeError:
            # Fallback: try to extract JSON from text
            data = self._extract_json_from_text(response_text)
            if not data:
                return MenuExtractResponse(
                    success=False,
                    error_message="AI 回傳格式無法解析",
                    warnings=["建議重新上傳更清晰的圖片"],
                )

        # Validate categories
        categories = data.get("categories", [])
        validated_categories = self._sanitize_categories(categories)

        # Calculate stats and warnings
        warnings = []
        total_items = 0
        items_need_review = 0

        for cat in validated_categories:
            for item in cat.items:
                total_items += 1
                if item.price == 0:
                    items_need_review += 1
                    warnings.append(f"品項「{item.name}」價格為 0，請確認")

        return MenuExtractResponse(
            success=True,
            categories=validated_categories,
            raw_text=data.get("raw_text"),
            warnings=warnings,
            stats=ExtractionStats(
                total_items=total_items,
                items_need_review=items_need_review,
            ),
        )

    def _extract_json_from_text(self, text: str) -> dict[str, Any] | None:
        """Try to extract JSON object from text that may contain other content.

        Args:
            text: Text that may contain JSON

        Returns:
            Parsed JSON dict or None if extraction fails
        """
        # Try to find JSON object in text
        patterns = [
            r"\{[\s\S]*\}",  # Basic JSON object
            r"```json\s*([\s\S]*?)```",  # Markdown code block
            r"```\s*([\s\S]*?)```",  # Generic code block
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                json_str = match.group(1) if "```" in pattern else match.group(0)
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue

        return None

    def _sanitize_categories(
        self, categories: list[dict[str, Any]]
    ) -> list[ExtractedCategory]:
        """Sanitize and validate category data with fallback for invalid items.

        Args:
            categories: Raw category data from AI

        Returns:
            List of validated ExtractedCategory objects
        """
        validated = []

        for cat_data in categories:
            try:
                # Validate category name
                name = str(cat_data.get("name", "未分類"))[:50]
                if not name:
                    name = "未分類"

                # Validate items
                items = []
                for item_data in cat_data.get("items", []):
                    try:
                        item = ExtractedMenuItem(
                            name=str(item_data.get("name", ""))[:100],
                            price=float(item_data.get("price", 0)),
                            description=str(item_data.get("description", ""))[:500]
                            if item_data.get("description")
                            else None,
                        )
                        if item.name:  # Only add items with names
                            items.append(item)
                    except (ValueError, ValidationError):
                        # Skip invalid items
                        continue

                if items:  # Only add categories with items
                    validated.append(ExtractedCategory(name=name, items=items))

            except (ValueError, ValidationError):
                # Skip invalid categories
                continue

        return validated


class OpenAIMenuExtractor(MenuExtractorBase):
    """OpenAI GPT-4V implementation (placeholder for future expansion)."""

    async def extract(self, image_base64: str) -> MenuExtractResponse:
        """Not implemented yet."""
        return MenuExtractResponse(
            success=False,
            error_message="OpenAI GPT-4V 支援開發中",
            warnings=["請使用 Claude 作為 AI Provider"],
        )


class GeminiMenuExtractor(MenuExtractorBase):
    """Google Gemini implementation (placeholder for future expansion)."""

    async def extract(self, image_base64: str) -> MenuExtractResponse:
        """Not implemented yet."""
        return MenuExtractResponse(
            success=False,
            error_message="Google Gemini 支援開發中",
            warnings=["請使用 Claude 作為 AI Provider"],
        )


def get_menu_extractor(provider: AIProvider | None = None) -> MenuExtractorBase:
    """Factory function to get menu extractor instance.

    Args:
        provider: AI provider to use, defaults to settings.AI_PROVIDER

    Returns:
        MenuExtractorBase instance for the specified provider

    Raises:
        ValueError: If provider is not supported or API key is missing
    """
    # Get provider from settings if not specified
    if provider is None:
        provider_str = getattr(settings, "AI_PROVIDER", "claude")
        try:
            provider = AIProvider(provider_str)
        except ValueError:
            provider = AIProvider.CLAUDE

    if provider == AIProvider.CLAUDE:
        api_key = getattr(settings, "ANTHROPIC_API_KEY", None)
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY 環境變數未設定")
        return ClaudeMenuExtractor(api_key=api_key)

    elif provider == AIProvider.OPENAI:
        return OpenAIMenuExtractor()

    elif provider == AIProvider.GEMINI:
        return GeminiMenuExtractor()

    else:
        raise ValueError(f"不支援的 AI Provider: {provider}")

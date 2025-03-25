from lightrag import LightRAG
from lightrag.utils import setup_logger
from lightrag.llm.openai import openai_complete_if_cache, openai_embed

import asyncio
import numpy as np
from config import BASE_STORAGE_DIR, LLM_API_KEY, LLM_BASE_URL

setup_logger("lightrag", level="INFO")

async def init_rag(context_name: str) -> LightRAG:
    async def llm_model_func(
            prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs
    ) -> str:
        return await openai_complete_if_cache(
            "model_name",
            prompt,
            system_prompt=system_prompt,
            history_messages=history_messages,
            api_key=LLM_API_KEY,
            base_url=LLM_BASE_URL,
            **kwargs
        )
    # проверить на рабочем ноуте как там реализовано
    async def embedding_func(texts: list[str]) -> np.ndarray:
        return await openai_embed(
            texts,
            model="embed_model_name",
            api_key="123"
        )

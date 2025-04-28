# Файл: moduls/lightrag_module.py
from lightrag import LightRAG, QueryParam
from lightrag.llm.openai import openai_complete_if_cache
from lightrag.utils import setup_logger, EmbeddingFunc
from lightrag.llm.hf import hf_embed
from lightrag.kg.shared_storage import initialize_pipeline_status

# Возможно, потребуется импортировать initialize_pipeline_status, если оно асинхронное
# from lightrag.kg.shared_storage import initialize_pipeline_status

from transformers import AutoModel, AutoTokenizer
import asyncio # asyncio больше не нужен здесь для run
import numpy as np
from config import LLM_API_KEY, LLM_BASE_URL, MODEL_NAME, MAX_TOKEN_SIZE_EMBED, EMBED_TOKENIZER_NAME

setup_logger("lightrag", level="INFO")

# Сделать build_rag асинхронной функцией
async def build_rag(storage_dir: str):

    # Определим асинхронную функцию для модели LLM, как и было
    async def llm_model_func(
            prompt, system_prompt=None, history_messages=[], keyword_extraction=False, **kwargs) -> str:
        return await openai_complete_if_cache(
            MODEL_NAME,
            prompt,
            system_prompt=system_prompt,
            api_key=LLM_API_KEY,
            history_messages=history_messages,
            base_url=LLM_BASE_URL,
            **kwargs
        )

    # Создаем экземпляр LightRAG
    rag = LightRAG(
        working_dir=storage_dir,
        llm_model_func=llm_model_func, # Передаем async функцию
        llm_model_name=MODEL_NAME,
        embedding_func=EmbeddingFunc(
            embedding_dim=1024,
            max_token_size=MAX_TOKEN_SIZE_EMBED,
            func=lambda texts: hf_embed( # Убедись, что hf_embed может работать в async контексте (обычно да)
                texts,
                tokenizer=AutoTokenizer.from_pretrained(
                    EMBED_TOKENIZER_NAME, device_map="auto"
                ),
                embed_model=AutoModel.from_pretrained(
                    EMBED_TOKENIZER_NAME, device_map="auto"
                ),
            ),
        ),
    )

    # Напрямую вызываем асинхронные методы инициализации
    await rag.initialize_storages()
    await initialize_pipeline_status()

    # Если initialize_pipeline_status асинхронная, используй await
    # await initialize_pipeline_status()
    # Если она синхронная, вызывай как обычно:
    # initialize_pipeline_status()
    # В твоем исходном коде она вызывалась внутри async функции, так что скорее всего, она async:
    # Проверь документацию/исходники LightRAG для initialize_pipeline_status
    # Предположим, что она async:
    # await initialize_pipeline_status() # <--- Раскомментируй, если она действительно async

    # Возвращаем инициализированный объект rag
    return rag

# Убираем вложенную initialize_rag и вызов asyncio.run
from gigachat import GigaChat
from typing import Dict, Any, List
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv


class GigaChatClient:
    def __init__(self, auth_key: str):
        """
        Initialize GigaChat client with authentication key

        Args:
            auth_key (str): Authentication key for GigaChat API
        """
        self.client = GigaChat(credentials=auth_key, verify_ssl_certs=False)

    async def send_prompt(self, prompt: str) -> str:
        """
        Send a prompt to GigaChat and get the response

        Args:
            prompt (str): The prompt to send to GigaChat

        Returns:
            str: The response from GigaChat
        """
        try:
            response = await asyncio.to_thread(self.client.chat, prompt)
            return response.choices[0].message.content
        except Exception as e:
            raise Exception(f"Error sending prompt to GigaChat: {str(e)}")

    async def _calculate_price_dynamics(
        self, products: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Рассчитывает динамику изменения цен и других параметров

        Args:
            products (List[Dict[str, Any]]): Список товаров, отсортированный по времени

        Returns:
            Dict[str, Any]: Статистика по динамике изменений
        """
        if not products:
            return {}

        # Сортируем по дате создания
        sorted_products = sorted(products, key=lambda x: x["created_at"])

        # Получаем первый и последний товар
        first_product = sorted_products[0]
        last_product = sorted_products[-1]

        # Рассчитываем изменения
        price_change = last_product["sell_price"] - first_product["sell_price"]
        price_change_percent = (
            (price_change / first_product["sell_price"] * 100)
            if first_product["sell_price"] != 0
            else 0
        )

        quantity_change = (
            last_product["total_quantity"] - first_product["total_quantity"]
        )

        # Асинхронно вычисляем период в днях
        first_date = datetime.fromisoformat(first_product["created_at"])
        last_date = datetime.fromisoformat(last_product["created_at"])
        period_days = (last_date - first_date).days

        return {
            "price_change": price_change,
            "price_change_percent": price_change_percent,
            "quantity_change": quantity_change,
            "period_days": period_days,
            "first_price": first_product["sell_price"],
            "last_price": last_product["sell_price"],
            "first_quantity": first_product["total_quantity"],
            "last_quantity": last_product["total_quantity"],
        }

    async def analyze_product(self, product: Dict[str, Any]) -> str:
        """
        Анализирует текущее состояние товара и дает рекомендацию покупателю

        Args:
            product (Dict[str, Any]): Текущее состояние товара

        Returns:
            str: Анализ и рекомендация по товару
        """
        # Форматируем дату для более читаемого вывода
        created_at = datetime.fromisoformat(product["created_at"])
        formatted_date = created_at.strftime("%d.%m.%Y %H:%M")

        prompt = f"""
        Ты - AI-помощник для покупателей на маркетплейсах. Анализируй данные товара:

        Название: {product['name']}
        Артикул: {product['artikul']}
        ID товара: {product['id']}
        Дата обновления: {formatted_date}

        Текущие параметры:
        Цена продажи: {product['sell_price']} ₽
        Стандартная цена: {product['standart_price']} ₽
        Скидка: {((product['standart_price'] - product['sell_price']) / product['standart_price'] * 100):.1f}%
        Количество на складе: {product['total_quantity']} шт.
        Рейтинг: {product['rating']}/5
        Маркетплейс: {product['marketplace']}

        Оцени:

        1. Соотношение цена/качество:
           - Сравнение с рыночной ценой
           - Размер скидки
           - Качество товара по рейтингу

        2. Популярность и доступность:
           - Наличие на складе
           - Рейтинг товара
           - Актуальность данных

        3. Надежность продавца:
           - Рейтинг товара
           - Маркетплейс
           - Наличие товара

        4. Общую привлекательность товара:
           - Суммарная оценка всех факторов
           - Уникальные преимущества
           - Потенциальные риски

        Дай краткую рекомендацию покупателю: стоит ли приобрести товар. Ответ не менее 250 и не более 400 символов.
        """

        return await self.send_prompt(prompt)

    async def analyze_products_batch(
        self, product_history: List[Dict[str, Any]]
    ) -> str:
        """
        Анализирует историю изменений одного товара

        Args:
            product_history (List[Dict[str, Any]]): История изменений товара (список состояний товара в разное время)

        Returns:
            str: Анализ и рекомендация по товару
        """
        # Сортируем историю по дате
        sorted_history = sorted(product_history, key=lambda x: x["created_at"])

        # Формируем строку с историей изменений
        history_text = "История изменений товара:\n"
        for product in sorted_history:
            created_at = datetime.fromisoformat(product["created_at"])
            formatted_date = created_at.strftime("%d.%m.%Y %H:%M")
            history_text += f"""
Дата: {formatted_date}
Артикул: {product['artikul']}
Название: {product['name']}
Стандартная цена: {product['standart_price']} ₽
Цена продажи: {product['sell_price']} ₽
Скидка: {((product['standart_price'] - product['sell_price']) / product['standart_price'] * 100):.1f}%
Количество: {product['total_quantity']} шт.
Рейтинг: {product['rating']}/5
-------------------"""

        # Рассчитываем динамику изменений
        dynamics = await self._calculate_price_dynamics(sorted_history)

        # Добавляем историю и динамику в промпт
        prompt = f"""
Ты - опытный аналитик маркетплейса Wildberries. Проанализируй историю изменений товара и дай рекомендации покупателю. 
ВАЖНО: Твой ответ должен содержать СТРОГО от 250 до 500 слов - не меньше и не больше. Используй счетчик слов.

Данные для анализа:

{history_text}

Динамика изменений за {dynamics['period_days']} дней:
- Изменение цены: {dynamics['price_change']} ₽ ({dynamics['price_change_percent']:.1f}%)
- Изменение количества: {dynamics['quantity_change']} шт.
- Начальная цена: {dynamics['first_price']} ₽
- Конечная цена: {dynamics['last_price']} ₽
- Начальное количество: {dynamics['first_quantity']} шт.
- Конечное количество: {dynamics['last_quantity']} шт.

Структура анализа (каждый пункт должен быть раскрыт в 2-3 предложениях):

1. Анализ динамики цен:
   - Оценка текущей цены относительно исторических значений
   - Анализ размера и стабильности скидки
   - Прогноз возможного изменения цены

2. Анализ спроса и наличия:
   - Динамика изменения количества товара
   - Риск исчезновения из продажи
   - Популярность товара

3. Оценка качества и надежности:
   - Анализ рейтинга и его стабильности
   - Репутация продавца
   - Общее качество предложения

4. Итоговая рекомендация:
   - Оптимальное время для покупки
   - Оценка рисков
   - Четкий совет: покупать сейчас / подождать / отказаться

ОБЯЗАТЕЛЬНО: 
- Используй только факты из предоставленных данных
- Давай конкретные рекомендации
- Пиши четко и по делу
- Ответ должен быть не менее 250 и не более 500 слов
- Проверь количество слов перед отправкой

Формат ответа:
[Анализ динамики цен]
[Анализ спроса и наличия]
[Оценка качества и надежности]
[Итоговая рекомендация]
"""
        return await self.send_prompt(prompt)



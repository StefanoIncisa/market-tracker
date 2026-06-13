import anthropic
from tracker.services.base_service import BaseService
from tracker.repositories import NewsRepository, AssetRepository
from tracker.models.news import NewsArticle
import config


class AIAnalystService(BaseService):
    """
    Uses Claude AI to analyse market data, summarise news,
    and answer questions about your portfolio.
    Each operation gets its own database session.
    """

    def __init__(self):
        super().__init__()
        self.__client = anthropic.Anthropic(api_key=config.ANTHROPIC_API_KEY)
        self.__model = "claude-sonnet-4-6"

    def summarise_news(self, article: NewsArticle) -> NewsArticle:
        """
        Analyses a news article and updates it with summary,
        sentiment, affected assets, and portfolio impact.
        """
        try:
            prompt = f"""You are a financial analyst. Analyse this news article and respond in this exact format:

SUMMARY:
[2-3 sentence plain English summary of the article]

SENTIMENT:
[exactly one word: positive, negative, or neutral]

AFFECTED_ASSETS:
[comma separated list of ticker symbols affected, e.g. AAPL, TSLA, GC=F — or NONE if no specific assets]

IMPACT:
[1-2 sentences on how this could affect an investor holding these assets]

Article title: {article.title}
Article source: {article.source}
"""

            message = self.__client.messages.create(
                model=self.__model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            response = message.content[0].text
            return self._parse_and_save(article, response)

        except Exception as e:
            self._handle_error(e, f"Failed to analyse article: {article.title}")
            return article

    def _parse_and_save(self, article: NewsArticle, response: str) -> NewsArticle:
        """
        Protected — parses Claude's response and saves back to database
        using a fresh session to avoid threading conflicts.
        """
        session = self._get_session()
        try:
            lines = response.strip().split("\n")
            current_section = None
            sections = {
                "SUMMARY": [],
                "SENTIMENT": [],
                "AFFECTED_ASSETS": [],
                "IMPACT": []
            }

            for line in lines:
                line = line.strip()
                if line in sections:
                    current_section = line
                elif current_section and line:
                    sections[current_section].append(line)

            # Fetch a fresh copy of the article in this session
            from tracker.repositories import NewsRepository
            news_repo = NewsRepository(session)
            fresh_article = news_repo.get_by_id(article.id)

            if not fresh_article:
                return article

            fresh_article.summary = " ".join(sections["SUMMARY"]).strip()
            fresh_article.sentiment = " ".join(sections["SENTIMENT"]).strip().lower()
            fresh_article.impact_analysis = " ".join(sections["IMPACT"]).strip()

            assets_raw = " ".join(sections["AFFECTED_ASSETS"]).strip()
            if assets_raw and assets_raw.upper() != "NONE":
                fresh_article.affected_assets = [
                    a.strip() for a in assets_raw.split(",") if a.strip()
                ]
            else:
                fresh_article.affected_assets = []

            news_repo.update(fresh_article)
            return fresh_article

        except Exception as e:
            self._handle_error(e, "Failed to parse and save AI response")
            return article
        finally:
            session.close()

    def analyse_portfolio(self, holdings: list, price_data: dict) -> str:
        """Generates a portfolio analysis based on current holdings and prices."""
        try:
            if not holdings:
                return "No holdings in portfolio yet."

            holdings_text = "\n".join([
                f"- {h.asset.symbol}: {h.quantity} units at avg ${h.average_buy_price:.2f}"
                for h in holdings
            ])

            prices_text = "\n".join([
                f"- {symbol}: ${snapshot.price:.2f} ({snapshot.change_pct:+.2f}% today)"
                for symbol, snapshot in price_data.items()
            ])

            prompt = f"""You are a personal financial analyst.
Analyse this portfolio and give a concise, honest assessment.

HOLDINGS:
{holdings_text}

CURRENT PRICES:
{prices_text}

Give a 3-4 sentence analysis covering:
1. Overall portfolio performance today
2. Best and worst performing positions
3. Any notable risks or opportunities

Be direct and specific. Use actual numbers."""

            message = self.__client.messages.create(
                model=self.__model,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text

        except Exception as e:
            self._handle_error(e, "Failed to analyse portfolio")
            return "Portfolio analysis unavailable."

    def daily_summary(self, price_data: dict, recent_news: list) -> str:
        """Generates a morning briefing — market overview plus top news impact."""
        try:
            prices_text = "\n".join([
                f"- {symbol}: ${snapshot.price:.2f} ({snapshot.change_pct:+.2f}%)"
                for symbol, snapshot in price_data.items()
            ]) if price_data else "No price data yet."

            news_text = "\n".join([
                f"- {article.title} ({article.source})"
                for article in recent_news[:5]
            ]) if recent_news else "No recent news yet."

            prompt = f"""You are a financial markets analyst giving a morning briefing.

CURRENT MARKET PRICES:
{prices_text}

TOP NEWS:
{news_text}

Give a concise 4-5 sentence market briefing covering:
1. Overall market mood today
2. Most significant price movements
3. How the top news is driving markets
4. One thing to watch today

Be direct, specific, and use actual numbers."""

            message = self.__client.messages.create(
                model=self.__model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}]
            )

            return message.content[0].text

        except Exception as e:
            self._handle_error(e, "Failed to generate daily summary")
            return "Daily summary unavailable."

    def chat(self, user_message: str, price_data: dict, holdings: list, recent_news: list) -> str:
        """Answers a user question with full portfolio and market context."""
        try:
            prices_text = "\n".join([
                f"- {symbol}: ${snapshot.price:.2f} ({snapshot.change_pct:+.2f}%)"
                for symbol, snapshot in price_data.items()
            ]) if price_data else "No price data yet."

            holdings_text = "\n".join([
                f"- {h.asset.symbol}: {h.quantity} units at avg ${h.average_buy_price:.2f}"
                for h in holdings
            ]) if holdings else "No holdings yet."

            news_text = "\n".join([
                f"- {article.title}"
                for article in recent_news[:5]
            ]) if recent_news else "No recent news."

            system_prompt = f"""You are a personal financial analyst assistant.
You have access to the user's portfolio, current market prices, and recent news.
Be concise, direct, and specific. Always use actual numbers when available.

CURRENT PRICES:
{prices_text}

USER'S PORTFOLIO:
{holdings_text}

RECENT NEWS:
{news_text}"""

            message = self.__client.messages.create(
                model=self.__model,
                max_tokens=600,
                system=system_prompt,
                messages=[{"role": "user", "content": user_message}]
            )

            return message.content[0].text

        except Exception as e:
            self._handle_error(e, "Failed to process chat message")
            return "I'm unable to answer that right now. Please try again."
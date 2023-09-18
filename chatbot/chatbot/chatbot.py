"""Welcome to Pynecone! This file outlines the steps to create a basic app."""

from datetime import datetime

import pynecone as pc
from pynecone.base import Base
from langchain import LLMChain

from langchain.chat_models import ChatOpenAI

from langchain.prompts.chat import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
)

from langchain.schema import SystemMessage

import os

os.environ["OPENAI_API_KEY"] = open("appkey.txt", "r").read()

data =open("kakaosink.txt", "r").read()

def build_llm():
    system_instruction = SystemMessage(content="assistant는 개발자에게 도움을 주기 위한 챗봇으로써 동작한다. 사용자의 질문에 대해서 카카오싱크 문서를 참조하여 간략하게 요약하여 한국어로 작성한다.")
    human_template = """
    아래 질문에 대해서 3줄 요약 답변해줘
    --- 
    {text}
    """
    llm = ChatOpenAI(temperature=1)
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
    return LLMChain(llm=llm, prompt=ChatPromptTemplate.from_messages([system_instruction, data, human_message_prompt]))


def query_text_using_chatgpt(text) -> str:
    chain = build_llm()
    result = chain.run(text=text)

    print(result)
    # Return
    return result


class Message(Base):
    message: str
    created_at: str
    is_user: bool
    is_gpt: bool


class State(pc.State):
    text: str = ""

    """The app state."""
    messages: list[Message] = [Message(message="안녕하세요 챗봇 서비스를 시작합니다. 궁금하신 내용을 물어보세요?",
                                       created_at=datetime.now().strftime("%B %d, %Y %I:%M %p"),
                                       is_user=False,
                                       is_gpt=True)]

    def ask(self):
        self.messages = self.messages + [Message(message=self.text,
                                                 created_at=datetime.now().strftime("%B %d, %Y %I:%M %p"),
                                                 is_user=True,
                                                 is_gpt=False)]

        gpt_result = query_text_using_chatgpt(self.text)

        self.messages = self.messages + [Message(message=gpt_result,
                                                 created_at=datetime.now().strftime("%B %d, %Y %I:%M %p"),
                                                 is_user=False,
                                                 is_gpt=True)]


# Define views.

def header():
    """Basic instructions to get started."""
    return pc.box(
        pc.text("카카오 싱크 챗봇 🗺", font_size="2rem"),
        pc.text(
            "chatbot system",
            margin_top="0.5rem",
            color="#666",
        ),
    )


def down_arrow():
    return pc.vstack(
        pc.icon(
            tag="arrow_down",
            color="#666",
        )
    )


def text_box(message):
    if message.is_gpt:
        return pc.text(
            message.message,
            background_color="#fff",
            padding="1rem",
            border_radius="8px",
        )
    else:
        return pc.text(
            message.message,
            background_color="#111",
            padding="1rem",
            border_radius="8px",
        )


def gpt_message_box(message):
    return pc.box(
        pc.vstack(
            text_box(message),
            spacing="0.3rem",
            align_items="left",
        ),
        background_color="#f5f5f5",
        padding="1rem",
        border_radius="8px")


def index():
    """The main view."""
    return pc.container(
        header(),
        pc.input(
            on_blur=State.set_text,
            placeholder="Ask any question...",
            border_color="#eaeaef",
        ),
        pc.button(
            "질문하기", on_click=State.ask
        ),
        pc.vstack(
            pc.foreach(State.messages, gpt_message_box),
            margin_top="2rem",
            spacing="1rem",
            align_items="left"
        ),
        padding="2rem",
        max_width="600px"
    )

    return message_boxes


# Add state and page to the app.

app = pc.App(state=State)
app.add_page(index, title="카카오싱크 챗봇")
app.compile()

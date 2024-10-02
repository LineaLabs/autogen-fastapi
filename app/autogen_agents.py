from autogen import ChatResult, GroupChat, Agent, OpenAIWrapper, ConversableAgent, UserProxyAgent, GroupChatManager
from data_model import ModelInformation
import os

config_list = [{
  "model": os.getenv("LLM_MODEL", "qwen-plus"),
  "base_url": os.getenv("BASE_URL","https://dashscope.aliyuncs.com/compatible-mode/v1"),
  "api_key": os.getenv("API_KEY","EMPTY"),
  "price" : [0.004, 0.012]
}]

llm_config = {"config_list": config_list, "cache_seed": 42}

agent_configs = {
  "article_writer": {
    "name": "ArticleWriter",
    "description": "默认的文章生成器，先根据需求描述生成文章提纲，然后根据提纲生成文章。",
    "agents": [
        {
            "type": "ConversableAgent",
            "name": "writer",
            "system_message": "根据editor提供的文章主题和大纲内容写作文章正文，正文应该是一段或多段文字，而不是大纲式列表，写作完成后将内容提交给editor检查，如果editor提出修改建议，则按要求修改，直到文章完成。",
            "human_input_mode": "NEVER",
            "code_execution_config": False,
            "llm_config": llm_config
        },
        {
            "type": "ConversableAgent",
            "name": "editor",
            "system_message": """分析并理解user提出的文章撰写要求，构思文章大纲和标题，然后通过多次对话依次将大纲的每个部分交给writer，要求writer根据大纲撰写该章节内容。
            writer写作完每一部分后你都要检查是否符合主题和字数要求，不符合要求的提出修改建议，如此依次重复直到全部章节写作完成。
            文章完成后将写作文章的全文汇总并包含在<article></article>标记中输出，然后结束对话并输出 TERMINATE""",
            "human_input_mode": "NEVER",
            "code_execution_config": False,
            "llm_config": llm_config
        }
    ]
  }
}

models = {}

for k, v in agent_configs.items():
    models[k] = ModelInformation(
        id=k,
        name=v["name"],
        description=v["description"],
        pricing={
            "prompt": "0.00",
            "completion": "0.00",
            "image": "0.00",
            "request": "0.00",
        },
        context_length=1024 * 1000,
        architecture={
            "modality": "text",
            "tokenizer": "text2vec-openai",
            "instruct_type": "InstructGPT",
        },
        top_provider={"max_completion_tokens": None, "is_moderated": False},
        per_request_limits=None
    )

def build_agents(agent_id):
    """ Must return a user_proxy agent at first place """
    agents = []
    agents.append(ConversableAgent(
      name="user",
      system_message="提出写作要求的用户。",
      is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
      code_execution_config= False,
      human_input_mode="NEVER"
    ))
    for config in agent_configs[agent_id]["agents"]:
      agents.append(
          ConversableAgent(
              name=config["name"],
              system_message=config["system_message"],
              human_input_mode=config["human_input_mode"],
              code_execution_config=config["code_execution_config"],
              llm_config=config["llm_config"],
          )
      )
    return agents
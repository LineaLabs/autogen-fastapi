from autogen import ChatResult, GroupChat, Agent, OpenAIWrapper, ConversableAgent, UserProxyAgent, GroupChatManager
from data_model import ModelInformation
import os
# 导入json依赖库
import json

config_list = [{
  "model": os.getenv("LLM_MODEL", "qwen-plus"),
  "base_url": os.getenv("BASE_URL","https://dashscope.aliyuncs.com/compatible-mode/v1"),
  "api_key": os.getenv("API_KEY","EMPTY"),
  "price" : [0.004, 0.012]
}]

llm_config = {"config_list": config_list, "cache_seed": 42, "timeout": 180}

# 读取 JSON 文件，初始化agent_configs
def load_agent(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        agent_configs = json.load(file)
        for agent_group_name, config in agent_configs.items():
            for agent in config['agents']:
                agent['llm_config'] = llm_config
    return agent_configs

agent_configs = load_agent('/app/app/agent_configs.json')

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
      _agent = ConversableAgent(
              name=config["name"],
              system_message=config["system_message"],
              human_input_mode=config["human_input_mode"],
              code_execution_config=config["code_execution_config"],
              llm_config=config["llm_config"],
          )
      agents.append(_agent)
    return agents
"""大模型诊断意见生成服务 — 兼容OpenAI/Anthropic及国内模型"""


def generate_diagnosis_opinion(ai_result, ai_confidence, risk_level, bbox, config=None):
    """调用LLM API生成诊断参考意见，失败时返回None不影响主流程

    config: Flask app.config 字典，包含 LLM_API_KEY / LLM_PROVIDER / LLM_BASE_URL / LLM_MODEL
    """
    if config is None:
        import os
        config = {
            'LLM_API_KEY': os.environ.get('LLM_API_KEY', ''),
            'LLM_PROVIDER': os.environ.get('LLM_PROVIDER', 'openai'),
            'LLM_BASE_URL': os.environ.get('LLM_BASE_URL', ''),
            'LLM_MODEL': os.environ.get('LLM_MODEL', 'gpt-4o'),
        }

    api_key = config.get('LLM_API_KEY', '')
    if not api_key:
        print("[LLM] 未配置LLM_API_KEY，跳过AI意见生成")
        return None

    provider = config.get('LLM_PROVIDER', 'openai')
    base_url = config.get('LLM_BASE_URL', '')
    model = config.get('LLM_MODEL', 'gpt-4o')

    # 结节信息描述
    bbox_info = f"位置(x={bbox['x']}, y={bbox['y']}), 尺寸(w={bbox['w']}px, h={bbox['h']}px)" if bbox.get('w') and bbox.get('h') else "未检测到明确结节位置"
    result_cn = '恶性' if ai_result == 'malignant' else '良性'
    risk_cn = {'low': '低风险', 'medium': '中风险', 'high': '高风险'}.get(risk_level, '未知')

    # 基于分类结果的模板描述
    templates = {
        ('benign', 'low'): '超声图像显示甲状腺结节形态规则，边界清晰，纵横比正常，回声均匀，符合良性结节特征。',
        ('benign', 'medium'): '超声图像显示甲状腺结节以良性特征为主，但存在部分可疑征象（如轻度低回声或边界欠清），需定期随访。',
        ('malignant', 'medium'): '超声图像显示甲状腺结节存在可疑恶性征象，如纵横比增大、边界不规则或低回声，建议进一步检查。',
        ('malignant', 'high'): '超声图像显示甲状腺结节高度可疑恶性，表现为明显纵向生长、边界模糊不规则、极低回声，强烈建议穿刺活检。',
    }
    template = templates.get((ai_result, risk_level), templates.get((ai_result, 'medium'), ''))

    prompt = f"""你是一位资深超声科医生，请根据以下甲状腺超声AI检测结果和初步描述，撰写一段专业的诊断参考意见（80-150字），包含结节特征描述和临床建议。

AI检测结果：
- 结节分类：{result_cn}
- 置信度：{ai_confidence:.1%}
- 风险等级：{risk_cn}
- 结节{bbox_info}

初步描述：{template}

请基于以上信息，给出完整的诊断参考意见，语言专业简洁，包含：1)结节超声特征 2)分类判断依据 3)临床处置建议。"""

    if provider == 'anthropic':
        return _call_anthropic(api_key, base_url, model, prompt)
    else:
        return _call_openai(api_key, base_url, model, prompt)


def _call_openai(api_key, base_url, model, prompt):
    """OpenAI及兼容接口（chat/completions）"""
    try:
        from openai import OpenAI

        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        client = OpenAI(**client_kwargs)
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
            max_tokens=300
        )
        opinion = response.choices[0].message.content.strip()
        print(f"[LLM] AI意见生成成功 (OpenAI兼容, model={model})")
        return opinion

    except ImportError:
        print("[LLM] openai SDK未安装，请执行: pip install openai")
        return None
    except Exception as e:
        print(f"[LLM] AI意见生成失败: {e}")
        return None


def _call_anthropic(api_key, base_url, model, prompt):
    """Anthropic Messages API 及兼容接口"""
    try:
        import anthropic

        client_kwargs = {"api_key": api_key}
        if base_url:
            client_kwargs["base_url"] = base_url

        client = anthropic.Anthropic(**client_kwargs)
        response = client.messages.create(
            model=model,
            max_tokens=300,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        # 过滤出TextBlock，跳过ThinkingBlock
        text_blocks = [b for b in response.content if hasattr(b, 'text')]
        if not text_blocks:
            print("[LLM] 未获取到文本响应")
            return None
        opinion = text_blocks[0].text.strip()
        print(f"[LLM] AI意见生成成功 (Anthropic, model={model})")
        return opinion

    except ImportError:
        print("[LLM] anthropic SDK未安装，请执行: pip install anthropic")
        return None
    except Exception as e:
        print(f"[LLM] AI意见生成失败: {e}")
        return None

# feishu_notifier.py
import requests
import json

def send_feishu_card(webhook_url: str, job_info: dict, match_result: dict, tailored_bullets: list):
    """构造飞书交互卡片并发送"""
    score = match_result.get('score', 0)
    # 根据分数高低动态调整卡片顶部标题颜色 (green: >=85, wathet: >=75)
    header_template = "green" if score >= 85 else "wathet"
    
    card_payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {
                    "tag": "plain_text",
                    "content": f"🎯 【高匹配岗位推荐】{job_info['title']} - {job_info['company']}"
                },
                "template": header_template
            },
            "elements": [
                {
                    "tag": "div",
                    "fields": [
                        {
                            "is_short": True,
                            "text": {"tag": "lark_md", "content": f"**匹配得分：** {score} 分"}
                        },
                        {
                            "is_short": True,
                            "text": {"tag": "lark_md", "content": f"**薪资范围：** {job_info.get('salary', '面议')}"}
                        }
                    ]
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": f"**💡 评估诊断：**\n{match_result.get('reason', '')}\n\n"
                                   f"**✅ 命中的技能：** {', '.join(match_result.get('matched_skills', []))}\n"
                                   f"**⚠️ 建议补充词：** {', '.join(match_result.get('missing_skills', []))}"
                    }
                },
                {"tag": "hr"},
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": "**📝 建议简历针对性修改 (Tailored Bullets)：**\n" + 
                                   "\n".join([f"• {bullet}" for bullet in tailored_bullets])
                    }
                },
                {
                    "tag": "action",
                    "actions": [
                        {
                            "tag": "button",
                            "text": {"tag": "plain_text", "content": "🔗 马上查看岗位并投递"},
                            "type": "primary",
                            "url": job_info['url']
                        }
                    ]
                }
            ]
        }
    }

    response = requests.post(
        webhook_url,
        headers={"Content-Type": "application/json"},
        data=json.dumps(card_payload)
    )
    return response.status_code == 200
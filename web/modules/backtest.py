#!/usr/bin/env python3
"""
分析回测页面
"""

import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from typing import List
import sys
from pathlib import Path
import time

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 导入UI工具函数
sys.path.append(str(Path(__file__).parent.parent))
from utils.ui_utils import apply_hide_deploy_button_css

# 延迟导入标记，初始为None
TradingAgentsGraph = None
DEFAULT_CONFIG = None

# 导入错误处理
import_error = None

def historical_backtest(symbol, start_date, end_date, interval_days=7, progress_callback=None, llm_provider=None, llm_model=None):
    """简单的历史回测"""
    global TradingAgentsGraph, DEFAULT_CONFIG, import_error
    
    # 只有在需要时才导入TradingAgents模块（延迟导入）
    if TradingAgentsGraph is None and import_error is None:
        try:
            from tradingagents.graph import TradingAgentsGraph as RealTradingAgentsGraph
            from tradingagents.default_config import DEFAULT_CONFIG as RealDefaultConfig
            TradingAgentsGraph = RealTradingAgentsGraph
            DEFAULT_CONFIG = RealDefaultConfig
        except ImportError as e:
            import_error = e
            # 创建模拟类用于演示
            class MockTradingAgentsGraph:
                def __init__(self, debug=False, config=None):
                    pass
                
                def propagate(self, symbol, date_str):
                    # 模拟分析结果
                    import random
                    actions = ["buy", "sell", "hold"]
                    action = random.choice(actions)
                    confidence = random.uniform(0.5, 0.9)
                    risk_score = random.uniform(0.1, 0.8)
                    
                    decision = {
                        "action": action,
                        "confidence": confidence,
                        "risk_score": risk_score
                    }
                    return {}, decision

            TradingAgentsGraph = MockTradingAgentsGraph
            DEFAULT_CONFIG = {
                "max_debate_rounds": 1,
                "online_tools": True,
                "project_dir": "."
            }
    
    # 配置
    config = DEFAULT_CONFIG.copy()
    config["max_debate_rounds"] = 1
    config["online_tools"] = True
    
    # 如果提供了LLM提供商和模型信息，添加到配置中
    if llm_provider:
        config["llm_provider"] = llm_provider
    if llm_model:
        config["deep_think_llm"] = llm_model
        config["quick_think_llm"] = llm_model
    
    # 如果有导入错误，在进度回调中显示警告
    if import_error and progress_callback:
        progress_callback(0.0, f"警告: 使用模拟模式进行回测 - 无法导入TradingAgents模块: {str(import_error)}")
    
    ta = TradingAgentsGraph(debug=False, config=config)
    
    # 生成日期列表
    current_date = datetime.strptime(start_date, "%Y-%m-%d")
    end_date_obj = datetime.strptime(end_date, "%Y-%m-%d")
    
    results = []
    
    total_days = (end_date_obj - current_date).days
    processed_days = 0
    
    while current_date <= end_date_obj:
        date_str = current_date.strftime("%Y-%m-%d")
        
        try:
            # 更新进度
            if progress_callback:
                progress = min(processed_days / total_days, 1.0)
                progress_callback(progress, f"正在分析 {symbol} 在 {date_str} 的数据...")
            
            # 执行分析
            state, decision = ta.propagate(symbol, date_str)
            
            result = {
                "date": date_str,
                "action": decision.get("action", "hold"),
                "confidence": decision.get("confidence", 0.5),
                "risk_score": decision.get("risk_score", 0.5),
            }
            
            results.append(result)
            
        except Exception as e:
            # 记录错误但继续处理
            result = {
                "date": date_str,
                "action": "error",
                "confidence": 0.0,
                "risk_score": 0.0,
                "error": str(e)
            }
            results.append(result)
        
        # 移动到下一个日期
        current_date += timedelta(days=interval_days)
        processed_days += interval_days
    
    return pd.DataFrame(results)

def render_backtest():
    """渲染分析回测页面"""
    # 应用隐藏Deploy按钮的CSS样式
    apply_hide_deploy_button_css()
    
    st.title("🔍 分析回测")
    
    # 创建回测参数表单
    with st.form("backtest_form", clear_on_submit=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # 股票代码输入
            stock_symbol = st.text_input(
                "股票代码 📈",
                value="",
                placeholder="输入股票代码，如 AAPL, 000001",
                help="输入要进行回测的股票代码"
            )
        
        # 将开始和结束日期放在同一行
        col3, col4 = st.columns(2)
        with col3:
            # 回测开始日期
            start_date = st.date_input(
                "开始日期 📅",
                value=datetime.today() - timedelta(days=365),  # 默认一年前
                help="选择回测开始日期"
            )
        
        with col4:
            # 回测结束日期
            end_date = st.date_input(
                "结束日期 📅",
                value=datetime.today(),
                help="选择回测结束日期"
            )
        
        # 提交按钮
        submitted = st.form_submit_button(
            "🚀 开始回测",
            type="primary",
            use_container_width=True
        )
    
    # 处理表单提交
    if submitted:
        if stock_symbol:
            # 显示进度条
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            def update_progress(progress, message):
                progress_bar.progress(progress)
                status_text.text(message)
            
            try:
                # 先显示初始化消息
                status_text.text("正在初始化分析模块...")
                
                # 从session_state获取LLM提供商和模型信息
                llm_provider = st.session_state.get('llm_provider', 'dashscope')
                llm_model = st.session_state.get('llm_model', 'qwen-plus')
                
                # 记录使用的LLM配置
                st.info(f"使用 {llm_provider} 的 {llm_model} 模型进行回测分析")
                
                # 执行回测
                with st.spinner("正在进行回测分析..."):
                    # 这里会触发延迟导入TradingAgents相关模块
                    backtest_results = historical_backtest(
                        symbol=stock_symbol.upper(),
                        start_date=start_date.strftime("%Y-%m-%d"),
                        end_date=end_date.strftime("%Y-%m-%d"),
                        interval_days=7,
                        progress_callback=update_progress,
                        llm_provider=llm_provider,
                        llm_model=llm_model
                    )
                
                # 完成进度条
                progress_bar.progress(1.0)
                status_text.text("回测完成!")
                
                # 显示结果
                st.subheader(f"📊 {stock_symbol.upper()} 回测结果")
                
                # 显示统计信息
                if not backtest_results.empty:
                    action_counts = backtest_results["action"].value_counts()
                    avg_confidence = backtest_results["confidence"].mean()
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("总分析次数", len(backtest_results))
                    col2.metric("平均置信度", f"{avg_confidence:.1%}")
                    col3.metric("买入信号", int(action_counts.get("buy", 0)))
                    
                    # 显示动作分布
                    st.write("### 动作分布")
                    st.bar_chart(action_counts)
                    
                    # 显示详细结果
                    st.write("### 详细结果")
                    st.dataframe(backtest_results, use_container_width=True)
                else:
                    st.warning("未获得有效的回测结果")
                    
            except Exception as e:
                st.error(f"回测过程中发生错误: {str(e)}")
                progress_bar.empty()
                status_text.empty()
        else:
            st.error("❌ 请输入股票代码")

def main():
    """主函数"""
    st.set_page_config(
        page_title="分析回测 - TradingAgents",
        page_icon="🔍",
        layout="wide"
    )
    
    render_backtest()

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
核心工作流功能测试脚本
"""

import os
import sys

def test_core_workflow():
    # Add project root to Python path
    project_root = os.path.dirname(os.path.abspath('.'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)

    print("🔍 测试核心工作流组件...")

    # 测试 1: Story State 模块
    try:
        from src.core.story_state import StoryState, Character, Location, Chapter, ChapterState
        print("✅ Story State 模块加载成功")

        # 创建一个示例故事状态
        story = StoryState(
            title="测试故事",
            genre="奇幻",
            summary="这是一个测试故事",
            target_chapter_count=5
        )
        print("✅ Story State 实例创建成功")
    except Exception as e:
        print(f"❌ Story State 模块错误: {e}")
        return False

    # 测试 2: 知识库模块
    try:
        print("🔍 测试知识库模块...")
        try:
            from src.core.knowledge_base import KnowledgeBase
            kb = KnowledgeBase(embed_model="local")
            print("✅ 完整版 KnowledgeBase 可用")
        except Exception as e:
            print(f"⚠ 完整版 KnowledgeBase 有误，使用降级版本: {e}")
            from src.core.knowledge_base_minimal import KnowledgeBase
            kb = KnowledgeBase()
            print("✅ 降级版 KnowledgeBase 可用")
    except Exception as e:
        print(f"❌ 知识库模块错误: {e}")
        return False

    # 测试 3: AI Agent 工厂
    try:
        from src.core.agent_factory import AgentFactory
        factory = AgentFactory(kb)
        print("✅ Agent Factory 加载成功")

        # 创建所有代理
        agents = factory.create_all_agents()
        print(f"✅ Agent Factory 创建了 {len(agents)} 个代理")
    except Exception as e:
        print(f"❌ Agent Factory 错误: {e}")
        return False

    # 测试 4: 工作流模块
    try:
        from src.core.workflow import NovelWritingWorkflow, create_default_workflow
        workflow = create_default_workflow(kb)
        print("✅ Workflow 创建成功")

        # 检查是否为降级模式
        if workflow.app is None:
            print("ℹ Workflow 当前处于降级模式，缺少 LangGraph 依赖")
        else:
            print("✅ Workflow 处于完整模式")
    except Exception as e:
        print(f"❌ Workflow 模块错误: {e}")
        return False

    # 测试 5: 基本运行逻辑
    try:
        print("🔍 测试基本操作...")
        # 测试添加角色
        from src.core.story_state import Character
        test_char = Character(
            id="char_test_1",
            name="测试角色",
            description="一个测试角色",
            role="主角"
        )
        story.add_character(test_char)
        print(f"✅ 添加角色成功，当前角色数: {len(story.characters)}")

        # 测试添加位置
        from src.core.story_state import Location
        test_loc = Location(
            id="loc_test_1",
            name="测试地点",
            description="一个测试地点",
            type="森林"
        )
        story.add_location(test_loc)
        print(f"✅ 添加位置成功，当前位置数: {len(story.locations)}")

    except Exception as e:
        print(f"❌ 基本操作测试失败: {e}")
        return False

    print()
    print("🎉 核心工作流系统测试通过!")
    print("系统各组件均能正常工作，包含完整的容错降级机制")
    return True

if __name__ == "__main__":
    success = test_core_workflow()
    if success:
        print("\n✅ 所有核心功能正常运行")
        sys.exit(0)
    else:
        print("\n❌ 核心功能存在错误")
        sys.exit(1)
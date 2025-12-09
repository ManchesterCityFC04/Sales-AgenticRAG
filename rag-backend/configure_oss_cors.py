#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
配置OSS Bucket的CORS规则
"""

import os
import sys
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def configure_cors():
    """配置OSS CORS规则"""
    print("=" * 60)
    print("配置OSS Bucket CORS规则")
    print("=" * 60)
    
    # 加载环境变量
    env_path = os.path.join(os.path.dirname(__file__), 'backend', '.env')
    load_dotenv(env_path)
    
    try:
        import alibabacloud_oss_v2 as oss
        from backend.config.oss import OssClientFactory
        
        bucket_name = os.getenv('OSS_BUCKET_NAME', 'wangwenzheng')
        print(f"\nBucket: {bucket_name}\n")
        
        # 获取OSS客户端
        client = OssClientFactory.get_client()
        
        # 定义CORS规则
        cors_rule = oss.models.CORSRule(
            allowed_origins=['*'],  # 允许所有来源，生产环境建议指定具体域名
            allowed_methods=['GET', 'POST', 'PUT', 'DELETE', 'HEAD'],
            allowed_headers=['*'],
            expose_headers=['ETag', 'x-oss-request-id', 'x-oss-version-id'],
            max_age_seconds=3600
        )
        
        # 设置CORS配置
        cors_config = oss.models.CORSConfiguration(
            cors_rules=[cors_rule]
        )
        
        # 应用CORS配置
        request = oss.PutBucketCorsRequest(
            bucket=bucket_name,
            cors_configuration=cors_config
        )
        
        result = client.put_bucket_cors(request)
        
        print("✓ CORS规则配置成功!")
        print("\n配置详情:")
        print("  允许来源: *")
        print("  允许方法: GET, POST, PUT, DELETE, HEAD")
        print("  允许Headers: *")
        print("  暴露Headers: ETag, x-oss-request-id, x-oss-version-id")
        print("  缓存时间: 3600秒")
        
        print("\n" + "=" * 60)
        print("验证CORS配置")
        print("=" * 60)
        
        # 读取并验证配置
        get_request = oss.GetBucketCorsRequest(bucket=bucket_name)
        get_result = client.get_bucket_cors(get_request)
        
        if get_result.cors_configuration and get_result.cors_configuration.cors_rules:
            print(f"\n✓ 已配置 {len(get_result.cors_configuration.cors_rules)} 条CORS规则")
            
            for i, rule in enumerate(get_result.cors_configuration.cors_rules, 1):
                print(f"\n规则 {i}:")
                print(f"  允许来源: {', '.join(rule.allowed_origins or [])}")
                print(f"  允许方法: {', '.join(rule.allowed_methods or [])}")
                if rule.allowed_headers:
                    print(f"  允许Headers: {', '.join(rule.allowed_headers)}")
                if rule.expose_headers:
                    print(f"  暴露Headers: {', '.join(rule.expose_headers)}")
                if rule.max_age_seconds:
                    print(f"  缓存时间: {rule.max_age_seconds}秒")
        
        print("\n✓ 配置完成！现在可以尝试前端上传了。")
        return True
        
    except Exception as e:
        print(f"\n✗ 配置失败: {e}")
        print("\n请尝试通过阿里云控制台手动配置CORS:")
        print("1. 访问: https://oss.console.aliyun.com/")
        print("2. 选择bucket: wangwenzheng")
        print("3. 权限管理 → 跨域设置（CORS）")
        print("4. 创建规则，配置如上所示")
        
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 17 + "OSS CORS配置工具" + " " * 21 + "║")
    print("╚" + "═" * 58 + "╝")
    print()
    
    success = configure_cors()
    
    if success:
        print("\n" + "=" * 60)
        print("后续步骤")
        print("=" * 60)
        print("\n1. 刷新前端页面（Ctrl+F5 强制刷新）")
        print("2. 尝试上传文件")
        print("3. 检查浏览器控制台是否还有错误")
        print()
    
    sys.exit(0 if success else 1)


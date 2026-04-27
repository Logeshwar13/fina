#!/usr/bin/env python3
"""
Quick verification script to check if everything is ready to run.
Run this before starting the application to verify your setup.
"""

import os
import sys
from pathlib import Path

def check_file(path, description):
    """Check if a file exists"""
    if os.path.exists(path):
        print(f"✅ {description}: Found")
        return True
    else:
        print(f"❌ {description}: NOT FOUND")
        return False

def check_env_var(var_name):
    """Check if environment variable is set"""
    value = os.getenv(var_name)
    if value and value != "your_value_here":
        print(f"✅ {var_name}: Set")
        return True
    else:
        print(f"❌ {var_name}: NOT SET or using placeholder")
        return False

def main():
    print("=" * 60)
    print("FinA Setup Verification")
    print("=" * 60)
    print()
    
    all_good = True
    
    # Check ML Models
    print("📊 Checking ML Models...")
    models = [
        ("backend/ml/models/category_classifier.pkl", "Transaction Categorization Model"),
        ("backend/ml/models/tfidf_vectorizer.pkl", "TF-IDF Vectorizer"),
        ("backend/ml/models/fraud_model.pkl", "Fraud Detection Model"),
        ("backend/ml/models/fraud_scaler.pkl", "Fraud Model Scaler"),
    ]
    
    for path, desc in models:
        if not check_file(path, desc):
            all_good = False
    print()
    
    # Check Environment File
    print("🔧 Checking Environment Configuration...")
    if check_file("backend/.env", "Environment file (.env)"):
        # Load .env file
        try:
            from dotenv import load_dotenv
            load_dotenv("backend/.env")
            
            # Check required variables
            required_vars = [
                "SUPABASE_URL",
                "SUPABASE_KEY",
                "GROQ_API_KEY"
            ]
            
            for var in required_vars:
                if not check_env_var(var):
                    all_good = False
        except ImportError:
            print("⚠️  python-dotenv not installed, skipping env var check")
    else:
        print("❌ Environment file not found!")
        print("   Run: cp backend/.env.example backend/.env")
        print("   Then edit backend/.env with your credentials")
        all_good = False
    print()
    
    # Check Docker
    print("🐳 Checking Docker...")
    docker_check = os.system("docker --version > /dev/null 2>&1")
    if docker_check == 0:
        print("✅ Docker: Installed")
    else:
        print("❌ Docker: NOT INSTALLED")
        print("   Install from: https://docs.docker.com/get-docker/")
        all_good = False
    
    docker_compose_check = os.system("docker-compose --version > /dev/null 2>&1")
    if docker_compose_check == 0:
        print("✅ Docker Compose: Installed")
    else:
        print("❌ Docker Compose: NOT INSTALLED")
        all_good = False
    print()
    
    # Check Deploy Script
    print("📜 Checking Deploy Script...")
    if check_file("deploy.sh", "Deploy script"):
        if os.access("deploy.sh", os.X_OK):
            print("✅ Deploy script: Executable")
        else:
            print("⚠️  Deploy script: Not executable")
            print("   Run: chmod +x deploy.sh")
    else:
        all_good = False
    print()
    
    # Check Docker Compose File
    print("🐳 Checking Docker Configuration...")
    check_file("docker-compose.yml", "Docker Compose configuration")
    check_file("Dockerfile", "Dockerfile")
    print()
    
    # Summary
    print("=" * 60)
    if all_good:
        print("✅ ALL CHECKS PASSED!")
        print()
        print("You're ready to run the application!")
        print()
        print("Next steps:")
        print("1. Run: ./deploy.sh up")
        print("2. Wait 30-60 seconds for startup")
        print("3. Open: http://localhost")
        print()
        print("That's it! Everything will initialize automatically.")
    else:
        print("❌ SOME CHECKS FAILED")
        print()
        print("Please fix the issues above before running.")
        print()
        print("Common fixes:")
        print("1. Copy environment file: cp backend/.env.example backend/.env")
        print("2. Edit backend/.env with your credentials")
        print("3. Install Docker: https://docs.docker.com/get-docker/")
        print("4. Make deploy script executable: chmod +x deploy.sh")
        print()
        print("If ML models are missing, run:")
        print("  cd backend && python data/train_models.py")
    print("=" * 60)
    
    return 0 if all_good else 1

if __name__ == "__main__":
    sys.exit(main())

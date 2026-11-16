import os
import sys
from pathlib import Path

base_dir = Path(__file__).resolve().parent
sys.path.append(str(base_dir))
sys.path.append(str(base_dir / "backend"))

from backend.app.config import SQLALCHEMY_DATABASE_URL
from backend.app.db import SessionLocal
from backend.app.models import User, Manuscript
from backend.app.security import get_password_hash

db = SessionLocal()

try:
    print("開始隨機建立或更新 User 與 Manuscript 資料...")

    # 1. 確保編輯者 host / 123 存在
    host_user = db.query(User).filter(User.username == "host").first()
    if not host_user:
        host_user = User(
            username="host",
            password_hash=get_password_hash("123"),
            role="editor"
        )
        db.add(host_user)
        db.commit()
        db.refresh(host_user)
        print("✅ 已建立編輯者帳號: host / 123 (role: editor)")
    else:
        host_user.password_hash = get_password_hash("123")
        host_user.role = "editor"
        db.commit()
        print("✅ 編輯者帳號 host 已存在，已更新密碼為 123")

    # 2. 隨機建立 2 筆作者 (符合：帳號密碼僅限英數字)
    author_samples = [
        {"username": "author01", "password": "author123password"},
        {"username": "writer88", "password": "pass8888"}
    ]

    created_authors = []
    for a in author_samples:
        user = db.query(User).filter(User.username == a["username"]).first()
        if not user:
            user = User(
                username=a["username"],
                password_hash=get_password_hash(a["password"]),
                role="author"
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"✅ 已建立作者帳號: {a['username']} / {a['password']} (role: author)")
        else:
            user.password_hash = get_password_hash(a["password"])
            db.commit()
            print(f"✅ 作者帳號 {a['username']} 已存在")
        created_authors.append(user)

    # 3. 隨機建立 3 筆稿件 (全中文，包含不同狀態)
    primary_author = created_authors[0]
    second_author = created_authors[1] if len(created_authors) > 1 else primary_author

    manuscript_samples = [
        {
            "author_id": primary_author.id,
            "category": "資訊科技",
            "title": "人工智慧技術在現代醫療影像診斷之應用與發展前景探討",
            "content": "隨著計算機運算能力的大幅躍升以及深度卷積神經網絡的蓬勃發展，醫學影像分析領域迎來了重大的變革。透過精準的特徵提取與模式識別，機器學習演算法在早期肺部結節篩檢以及視網膜病變檢測中展現出高度的敏銳度。未來結合臨床多模態數據的綜合判讀，將能進一步協助醫療團隊提高診療決策的效率與精準度。",
            "status": "draft",
            "reject_notice": None
        },
        {
            "author_id": primary_author.id,
            "category": "人文哲思",
            "title": "傳統東方水墨繪畫中的留白美學與意境營造解析",
            "content": "東方傳統水墨畫論講究虛實相生，計白當黑。畫面上的大片空白並非虛無，而是賦予觀者想像空間的悠遠意境。雲霧繚繞與山光水色在虛實掩映之間，流露出深沉的哲學意趣，展現人與自然和諧共生的寧靜心境。",
            "status": "review",
            "reject_notice": None
        },
        {
            "author_id": second_author.id,
            "category": "自然科學",
            "title": "深海熱泉生態系中極限微生物的化學合成機制研究",
            "content": "在陽光無法穿透的深海高壓環境中，熱泉噴口周邊繁衍著獨特的化學合成生態系統。以硫化氫為能量來源的化能合成細菌，形成了深海食物鏈的基礎生產者。對此類極限環境生物的研究，不僅拓展了生命科學對生存條件的認知，也為探索地外天體潛在生命提供了寶貴的線索。",
            "status": "approved",
            "reject_notice": None
        }
    ]

    for ms_data in manuscript_samples:
        existing_ms = db.query(Manuscript).filter(
            Manuscript.title == ms_data["title"],
            Manuscript.author_id == ms_data["author_id"]
        ).first()
        if not existing_ms:
            ms = Manuscript(**ms_data)
            db.add(ms)
            db.commit()
            print(f"✅ 已建立稿件: 《{ms_data['title']}》 [狀態: {ms_data['status']}]")
        else:
            print(f"ℹ️ 稿件已存在: 《{ms_data['title']}》")

    print("\n🎉 資料庫測試資料初始化完成！")

except Exception as e:
    db.rollback()
    print("❌ 建立資料失敗:", e)
    raise
finally:
    db.close()

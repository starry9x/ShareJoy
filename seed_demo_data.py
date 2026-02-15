"""
Database seeding script for ShareJoy demo groups.
This script ensures that two demo groups persist when the application is hosted.
"""

from extensions import db
from groups import Group, GroupMember, GroupPost, GroupComment, GroupChatMessage
from datetime import datetime, timedelta


def seed_demo_groups():
    """
    Seed the database with two demo groups that will persist in production.
    These groups are marked as demo groups and cannot be deleted by users.
    """

    # Check if demo groups already exist by exact name (case-insensitive)
    demo_group_names = ["Board games afternoon", "Walk and talk nature club"]
    existing_board_games = Group.query.filter(Group.name.ilike("board%games%afternoon")).first()
    existing_walk_talk = Group.query.filter(Group.name.ilike("walk%talk%nature%club")).first()

    # If both demo groups already exist, don't recreate them
    if existing_board_games and existing_walk_talk:
        print("Demo groups already exist. Skipping seeding.")
        return [existing_board_games, existing_walk_talk]

    # Mark any similar groups as demo groups to avoid duplicates
    similar_groups = Group.query.filter(
        (Group.name.ilike("board%games%afternoon")) |
        (Group.name.ilike("walk%talk%nature%club"))
    ).all()

    for group in similar_groups:
        group.is_demo = True
    db.session.commit()

    # If we have the groups already, return them
    if len(similar_groups) >= 2:
        print("Found similar groups, marked as demo. Skipping seeding.")
        return similar_groups

    demo_groups = []

    # ============================================
    # DEMO GROUP 1: Board Games Afternoon
    # ============================================

    group1 = Group(
        name="Board games afternoon",
        description="Join us for an afternoon of classic and modern tabletop games! From strategy games to party favorites, we have something for everyone. Friendly competition and laughter guaranteed. All skill levels welcome - whether you're a seasoned player or just starting out!",
        category="Social",
        youth_percentage=75,
        tags="games,social,fun,boardgames,cards,puzzles",
        current_participants=8,
        max_participants=40,
        privacy="Public",
        owner="ShareJoy Admin",
        buddy_system_enabled=True,
        image_url="default_group.jpg",
        is_demo=True,
        created_at=datetime.utcnow() - timedelta(days=30)
    )
    db.session.add(group1)
    db.session.flush()  # Get the ID without committing

    # Add demo members for Board Games group
    demo_members_group1 = [
        GroupMember(
            group_id=group1.id,
            user_name="Sarah Chen",
            mood_status="😊",
            joined_at=datetime.utcnow() - timedelta(days=25)
        ),
        GroupMember(
            group_id=group1.id,
            user_name="Michael Rodriguez",
            mood_status="🎮",
            joined_at=datetime.utcnow() - timedelta(days=20)
        ),
        GroupMember(
            group_id=group1.id,
            user_name="Emma Thompson",
            mood_status="😄",
            joined_at=datetime.utcnow() - timedelta(days=18)
        ),
        GroupMember(
            group_id=group1.id,
            user_name="David Kim",
            mood_status="🎲",
            joined_at=datetime.utcnow() - timedelta(days=15)
        ),
        GroupMember(
            group_id=group1.id,
            user_name="Lisa Anderson",
            mood_status="😊",
            joined_at=datetime.utcnow() - timedelta(days=12)
        ),
        GroupMember(
            group_id=group1.id,
            user_name="James Wilson",
            mood_status="🎯",
            joined_at=datetime.utcnow() - timedelta(days=10)
        ),
        GroupMember(
            group_id=group1.id,
            user_name="Priya Patel",
            mood_status="😃",
            joined_at=datetime.utcnow() - timedelta(days=8)
        ),
        GroupMember(
            group_id=group1.id,
            user_name="Tom Jackson",
            mood_status="🎲",
            joined_at=datetime.utcnow() - timedelta(days=5)
        )
    ]

    for member in demo_members_group1:
        db.session.add(member)

    # Add demo posts for Board Games group
    demo_posts_group1 = [
        GroupPost(
            group_id=group1.id,
            author="Sarah Chen",
            content="Just got the new Wingspan expansion! Can't wait to try it at our next game night. Who's in?",
            likes=5,
            created_at=datetime.utcnow() - timedelta(days=7)
        ),
        GroupPost(
            group_id=group1.id,
            author="Michael Rodriguez",
            content="Had an amazing time at last week's session! The Catan tournament was intense. Thanks everyone for the great games!",
            likes=8,
            created_at=datetime.utcnow() - timedelta(days=5)
        ),
        GroupPost(
            group_id=group1.id,
            author="Emma Thompson",
            content="For those who are new to board games, we'll be playing some easy-to-learn games this Saturday. Perfect for beginners!",
            likes=6,
            created_at=datetime.utcnow() - timedelta(days=3)
        )
    ]

    for post in demo_posts_group1:
        db.session.add(post)
    db.session.flush()

    # Add demo comments for Board Games group
    demo_comments_group1 = [
        GroupComment(
            post_id=demo_posts_group1[0].id,
            author="David Kim",
            content="Count me in! I love Wingspan!",
            created_at=datetime.utcnow() - timedelta(days=6)
        ),
        GroupComment(
            post_id=demo_posts_group1[1].id,
            author="Lisa Anderson",
            content="That was so much fun! Can't wait for the next one.",
            created_at=datetime.utcnow() - timedelta(days=4)
        ),
        GroupComment(
            post_id=demo_posts_group1[2].id,
            author="Priya Patel",
            content="Perfect! I'm bringing my friend who's never played board games before.",
            created_at=datetime.utcnow() - timedelta(days=2)
        )
    ]

    for comment in demo_comments_group1:
        db.session.add(comment)

    # Add demo chat messages for Board Games group
    demo_chat_messages_group1 = [
        GroupChatMessage(
            group_id=group1.id,
            username="Sarah Chen",
            content="Hi everyone! Welcome to our board games group!",
            timestamp=datetime.utcnow() - timedelta(days=25, hours=2)
        ),
        GroupChatMessage(
            group_id=group1.id,
            username="Michael Rodriguez",
            content="Thanks! Excited to join you all.",
            timestamp=datetime.utcnow() - timedelta(days=20, hours=5)
        ),
        GroupChatMessage(
            group_id=group1.id,
            username="Emma Thompson",
            content="What time are we meeting this Saturday?",
            timestamp=datetime.utcnow() - timedelta(days=2, hours=3)
        ),
        GroupChatMessage(
            group_id=group1.id,
            username="David Kim",
            content="I think it's at 2 PM. Looking forward to it!",
            timestamp=datetime.utcnow() - timedelta(days=2, hours=1)
        )
    ]

    for message in demo_chat_messages_group1:
        db.session.add(message)

    demo_groups.append(group1)

    # ============================================
    # DEMO GROUP 2: Walk and Talk Nature Club
    # ============================================

    group2 = Group(
        name="Walk and talk nature club",
        description="Gentle walks in neighbourhood parks with relaxed conversations and shared moments in nature. Perfect for all fitness levels. We explore local trails, enjoy fresh air, and build connections through meaningful conversations. Join us for mindful walks and peaceful moments in green spaces.",
        category="Wellness",
        youth_percentage=25,
        tags="wellness,nature,walking,community,outdoor,health",
        current_participants=10,
        max_participants=40,
        privacy="Public",
        owner="ShareJoy Admin",
        buddy_system_enabled=True,
        image_url="default_group.jpg",
        is_demo=True,
        created_at=datetime.utcnow() - timedelta(days=45)
    )
    db.session.add(group2)
    db.session.flush()

    # Add demo members for Walk and Talk group
    demo_members_group2 = [
        GroupMember(
            group_id=group2.id,
            user_name="Margaret Lee",
            mood_status="🌿",
            joined_at=datetime.utcnow() - timedelta(days=40)
        ),
        GroupMember(
            group_id=group2.id,
            user_name="Robert Brown",
            mood_status="🚶",
            joined_at=datetime.utcnow() - timedelta(days=35)
        ),
        GroupMember(
            group_id=group2.id,
            user_name="Jennifer Garcia",
            mood_status="🌳",
            joined_at=datetime.utcnow() - timedelta(days=30)
        ),
        GroupMember(
            group_id=group2.id,
            user_name="William Tan",
            mood_status="😊",
            joined_at=datetime.utcnow() - timedelta(days=28)
        ),
        GroupMember(
            group_id=group2.id,
            user_name="Catherine Wong",
            mood_status="🌸",
            joined_at=datetime.utcnow() - timedelta(days=25)
        ),
        GroupMember(
            group_id=group2.id,
            user_name="Daniel Martinez",
            mood_status="🌞",
            joined_at=datetime.utcnow() - timedelta(days=22)
        ),
        GroupMember(
            group_id=group2.id,
            user_name="Susan Taylor",
            mood_status="🌿",
            joined_at=datetime.utcnow() - timedelta(days=18)
        ),
        GroupMember(
            group_id=group2.id,
            user_name="Kevin Ng",
            mood_status="🚶",
            joined_at=datetime.utcnow() - timedelta(days=15)
        ),
        GroupMember(
            group_id=group2.id,
            user_name="Patricia Smith",
            mood_status="🌺",
            joined_at=datetime.utcnow() - timedelta(days=12)
        ),
        GroupMember(
            group_id=group2.id,
            user_name="Andrew Lim",
            mood_status="😄",
            joined_at=datetime.utcnow() - timedelta(days=8)
        )
    ]

    for member in demo_members_group2:
        db.session.add(member)

    # Add demo posts for Walk and Talk group
    demo_posts_group2 = [
        GroupPost(
            group_id=group2.id,
            author="Margaret Lee",
            content="Beautiful morning walk today at East Coast Park! The sunrise was absolutely stunning. Thank you everyone for the wonderful company and great conversations.",
            likes=12,
            created_at=datetime.utcnow() - timedelta(days=10)
        ),
        GroupPost(
            group_id=group2.id,
            author="Robert Brown",
            content="Next week we'll be exploring the Botanic Gardens. The orchids should be in full bloom! Remember to bring your water bottles and wear comfortable shoes.",
            likes=9,
            created_at=datetime.utcnow() - timedelta(days=6)
        ),
        GroupPost(
            group_id=group2.id,
            author="Jennifer Garcia",
            content="Loved our gentle walk along the MacRitchie trail yesterday. The nature therapy is real! Feeling so refreshed and energized.",
            likes=11,
            created_at=datetime.utcnow() - timedelta(days=4)
        ),
        GroupPost(
            group_id=group2.id,
            author="William Tan",
            content="For our newer members: We usually walk at a relaxed pace, stopping frequently to enjoy the scenery and chat. It's all about the journey, not the destination!",
            likes=7,
            created_at=datetime.utcnow() - timedelta(days=2)
        )
    ]

    for post in demo_posts_group2:
        db.session.add(post)
    db.session.flush()

    # Add demo comments for Walk and Talk group
    demo_comments_group2 = [
        GroupComment(
            post_id=demo_posts_group2[0].id,
            author="Catherine Wong",
            content="It was amazing! Already looking forward to our next walk.",
            created_at=datetime.utcnow() - timedelta(days=9)
        ),
        GroupComment(
            post_id=demo_posts_group2[0].id,
            author="Daniel Martinez",
            content="Thanks for organizing Margaret! Best way to start the day.",
            created_at=datetime.utcnow() - timedelta(days=9)
        ),
        GroupComment(
            post_id=demo_posts_group2[1].id,
            author="Susan Taylor",
            content="Can't wait! The Botanic Gardens is my favorite spot.",
            created_at=datetime.utcnow() - timedelta(days=5)
        ),
        GroupComment(
            post_id=demo_posts_group2[2].id,
            author="Kevin Ng",
            content="Same here! I slept so well last night after the walk.",
            created_at=datetime.utcnow() - timedelta(days=3)
        ),
        GroupComment(
            post_id=demo_posts_group2[3].id,
            author="Patricia Smith",
            content="This is exactly what I was looking for! Joining the next walk for sure.",
            created_at=datetime.utcnow() - timedelta(days=1)
        )
    ]

    for comment in demo_comments_group2:
        db.session.add(comment)

    # Add demo chat messages for Walk and Talk group
    demo_chat_messages_group2 = [
        GroupChatMessage(
            group_id=group2.id,
            username="Margaret Lee",
            content="Welcome everyone to our Walk and Talk Nature Club! Let's enjoy nature together.",
            timestamp=datetime.utcnow() - timedelta(days=40, hours=3)
        ),
        GroupChatMessage(
            group_id=group2.id,
            username="Robert Brown",
            content="Thanks for having me! Been looking for a walking group.",
            timestamp=datetime.utcnow() - timedelta(days=35, hours=6)
        ),
        GroupChatMessage(
            group_id=group2.id,
            username="Jennifer Garcia",
            content="What's the meeting point for this Sunday's walk?",
            timestamp=datetime.utcnow() - timedelta(days=3, hours=12)
        ),
        GroupChatMessage(
            group_id=group2.id,
            username="Margaret Lee",
            content="We'll meet at the Botanic Gardens main entrance at 7:30 AM.",
            timestamp=datetime.utcnow() - timedelta(days=3, hours=10)
        ),
        GroupChatMessage(
            group_id=group2.id,
            username="William Tan",
            content="Perfect! See you all there.",
            timestamp=datetime.utcnow() - timedelta(days=3, hours=8)
        )
    ]

    for message in demo_chat_messages_group2:
        db.session.add(message)

    demo_groups.append(group2)

    # Commit all changes
    try:
        db.session.commit()
        print(f"Successfully seeded {len(demo_groups)} demo groups:")
        for group in demo_groups:
            print(f"  - {group.name} (ID: {group.id})")
        return demo_groups
    except Exception as e:
        db.session.rollback()
        print(f"Error seeding demo groups: {str(e)}")
        raise


def check_and_seed_demo_groups():
    """
    Check if demo groups exist and seed them if they don't.
    This is a safe function to call on application startup.
    """
    # Check for existing demo groups by name (case-insensitive)
    existing_board_games = Group.query.filter(Group.name.ilike("board%games%afternoon")).first()
    existing_walk_talk = Group.query.filter(Group.name.ilike("walk%talk%nature%club")).first()

    if existing_board_games and existing_walk_talk:
        # Keep demo baseline ratios aligned even for old databases.
        has_updates = False

        if not existing_board_games.is_demo:
            existing_board_games.is_demo = True
            has_updates = True
        if not existing_walk_talk.is_demo:
            existing_walk_talk.is_demo = True
            has_updates = True
        if existing_board_games.youth_percentage != 75:  # 25% senior, 75% youth
            existing_board_games.youth_percentage = 75
            has_updates = True
        if existing_walk_talk.youth_percentage != 25:    # 75% senior, 25% youth
            existing_walk_talk.youth_percentage = 25
            has_updates = True

        if has_updates:
            db.session.commit()

        return [existing_board_games, existing_walk_talk]
    else:
        return seed_demo_groups()


if __name__ == "__main__":
    # This allows the script to be run standalone for testing
    from app import app

    with app.app_context():
        print("Starting demo data seeding...")
        seed_demo_groups()
        print("Demo data seeding completed!")

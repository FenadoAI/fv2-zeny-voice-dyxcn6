from fastapi import FastAPI, APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
import uuid
from datetime import datetime, timedelta
import jwt
import bcrypt


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'zeny_ai')]

# JWT Configuration
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_TIME = timedelta(hours=24)

# Admin Configuration
ADMIN_USERNAME = os.environ.get('ADMIN_USERNAME', 'admin')
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'admin')

# Security
security = HTTPBearer()

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")


# Define Models
class StatusCheck(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class StatusCheckCreate(BaseModel):
    client_name: str

# Zeny AI Models
class Avatar(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    personality: str
    description: str
    owner_id: str
    knowledge_base: Optional[str] = None
    avatar_image: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = True

class AvatarCreate(BaseModel):
    name: str
    personality: str
    description: str
    knowledge_base: Optional[str] = None
    avatar_image: Optional[str] = None

class AvatarUpdate(BaseModel):
    name: Optional[str] = None
    personality: Optional[str] = None
    description: Optional[str] = None
    knowledge_base: Optional[str] = None
    avatar_image: Optional[str] = None
    is_active: Optional[bool] = None

class Conversation(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    avatar_id: str
    participant_name: str
    messages: List[dict]
    started_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None
    status: str = "active"

class ConversationCreate(BaseModel):
    avatar_id: str
    participant_name: str

class Message(BaseModel):
    sender: str
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class Summary(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    avatar_id: str
    conversation_id: str
    summary_text: str
    key_points: List[str]
    generated_at: datetime = Field(default_factory=datetime.utcnow)

# Authentication Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: Optional[str] = None
    is_admin: bool = False
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UserCreate(BaseModel):
    username: str
    password: str
    email: Optional[str] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str
    user: User

class AdminCredentialsUpdate(BaseModel):
    new_username: str
    new_password: str

# Authentication Helper Functions
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + JWT_EXPIRATION_TIME
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    user = await db.users.find_one({"username": username})
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return User(**user)

async def get_admin_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

# Initialize admin user on startup
async def init_admin_user():
    admin_user = await db.users.find_one({"username": ADMIN_USERNAME})
    if not admin_user:
        hashed_password = hash_password(ADMIN_PASSWORD)
        admin_user_obj = User(
            username=ADMIN_USERNAME,
            email="admin@zeny.ai",
            is_admin=True
        )
        await db.users.insert_one({
            **admin_user_obj.dict(),
            "hashed_password": hashed_password
        })
        print(f"Admin user created: {ADMIN_USERNAME}")

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

# Authentication Endpoints
@api_router.post("/auth/login", response_model=Token)
async def login(user_login: UserLogin):
    user = await db.users.find_one({"username": user_login.username})
    if not user or not verify_password(user_login.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid username or password")
    
    access_token = create_access_token(data={"sub": user["username"]})
    user_obj = User(**{k: v for k, v in user.items() if k != "hashed_password"})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_obj
    }

@api_router.post("/auth/register", response_model=User)
async def register(user_create: UserCreate):
    existing_user = await db.users.find_one({"username": user_create.username})
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = hash_password(user_create.password)
    user_obj = User(
        username=user_create.username,
        email=user_create.email,
        is_admin=False
    )
    
    await db.users.insert_one({
        **user_obj.dict(),
        "hashed_password": hashed_password
    })
    
    return user_obj

@api_router.get("/auth/me", response_model=User)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@api_router.put("/auth/admin/credentials")
async def update_admin_credentials(
    credentials: AdminCredentialsUpdate,
    current_user: User = Depends(get_admin_user)
):
    global ADMIN_USERNAME, ADMIN_PASSWORD
    
    # Update the admin user in database
    hashed_password = hash_password(credentials.new_password)
    await db.users.update_one(
        {"username": current_user.username},
        {"$set": {
            "username": credentials.new_username,
            "hashed_password": hashed_password
        }}
    )
    
    # Update environment variables (for current session)
    ADMIN_USERNAME = credentials.new_username
    ADMIN_PASSWORD = credentials.new_password
    
    return {"message": "Admin credentials updated successfully"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

# Avatar Management Endpoints
@api_router.post("/avatars", response_model=Avatar)
async def create_avatar(avatar_data: AvatarCreate, current_user: User = Depends(get_current_user)):
    avatar_dict = avatar_data.dict()
    avatar_dict["owner_id"] = current_user.id  # Use authenticated user's ID
    avatar_obj = Avatar(**avatar_dict)
    await db.avatars.insert_one(avatar_obj.dict())
    return avatar_obj

@api_router.get("/avatars", response_model=List[Avatar])
async def get_avatars(current_user: User = Depends(get_current_user)):
    # Return avatars owned by the current user
    query = {"is_active": True, "owner_id": current_user.id}
    avatars = await db.avatars.find(query).to_list(1000)
    return [Avatar(**avatar) for avatar in avatars]

@api_router.get("/avatars/{avatar_id}", response_model=Avatar)
async def get_avatar(avatar_id: str, current_user: User = Depends(get_current_user)):
    avatar = await db.avatars.find_one({"id": avatar_id, "owner_id": current_user.id})
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    return Avatar(**avatar)

@api_router.put("/avatars/{avatar_id}", response_model=Avatar)
async def update_avatar(avatar_id: str, avatar_update: AvatarUpdate, current_user: User = Depends(get_current_user)):
    avatar = await db.avatars.find_one({"id": avatar_id, "owner_id": current_user.id})
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    update_data = {k: v for k, v in avatar_update.dict().items() if v is not None}
    if update_data:
        await db.avatars.update_one({"id": avatar_id}, {"$set": update_data})
    
    updated_avatar = await db.avatars.find_one({"id": avatar_id})
    return Avatar(**updated_avatar)

@api_router.delete("/avatars/{avatar_id}")
async def delete_avatar(avatar_id: str, current_user: User = Depends(get_current_user)):
    result = await db.avatars.update_one(
        {"id": avatar_id, "owner_id": current_user.id}, 
        {"$set": {"is_active": False}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Avatar not found")
    return {"message": "Avatar deleted successfully"}

# Conversation Management Endpoints
@api_router.post("/conversations", response_model=Conversation)
async def create_conversation(conversation_data: ConversationCreate):
    avatar = await db.avatars.find_one({"id": conversation_data.avatar_id, "is_active": True})
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    conversation_dict = conversation_data.dict()
    conversation_dict["messages"] = []
    conversation_obj = Conversation(**conversation_dict)
    await db.conversations.insert_one(conversation_obj.dict())
    return conversation_obj

@api_router.get("/conversations", response_model=List[Conversation])
async def get_conversations(avatar_id: Optional[str] = None):
    query = {}
    if avatar_id:
        query["avatar_id"] = avatar_id
    conversations = await db.conversations.find(query).to_list(1000)
    return [Conversation(**conversation) for conversation in conversations]

@api_router.get("/conversations/{conversation_id}", response_model=Conversation)
async def get_conversation(conversation_id: str):
    conversation = await db.conversations.find_one({"id": conversation_id})
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return Conversation(**conversation)

@api_router.post("/conversations/{conversation_id}/messages")
async def add_message(conversation_id: str, message: Message):
    conversation = await db.conversations.find_one({"id": conversation_id})
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    message_dict = message.dict()
    
    # Add the message to the conversation
    await db.conversations.update_one(
        {"id": conversation_id},
        {"$push": {"messages": message_dict}}
    )
    
    # If it's from a participant, generate AI response
    if message.sender != "avatar":
        avatar = await db.avatars.find_one({"id": conversation["avatar_id"]})
        if avatar:
            # Simple AI response generation (mock for now)
            ai_response = f"As {avatar['name']}, I understand your message about '{message.content[:50]}...'. Let me respond based on my personality: {avatar['personality'][:100]}..."
            
            ai_message = Message(
                sender="avatar",
                content=ai_response
            )
            
            await db.conversations.update_one(
                {"id": conversation_id},
                {"$push": {"messages": ai_message.dict()}}
            )
    
    return {"message": "Message added successfully"}

@api_router.put("/conversations/{conversation_id}/end")
async def end_conversation(conversation_id: str):
    result = await db.conversations.update_one(
        {"id": conversation_id},
        {"$set": {"status": "ended", "ended_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return {"message": "Conversation ended successfully"}

# Summary Management Endpoints
@api_router.post("/conversations/{conversation_id}/summary", response_model=Summary)
async def generate_summary(conversation_id: str):
    conversation = await db.conversations.find_one({"id": conversation_id})
    if not conversation:
        raise HTTPException(status_code=404, detail="Conversation not found")
    
    # Check if summary already exists
    existing_summary = await db.summaries.find_one({"conversation_id": conversation_id})
    if existing_summary:
        return Summary(**existing_summary)
    
    # Generate summary (mock implementation)
    messages = conversation.get("messages", [])
    participant_messages = [msg for msg in messages if msg["sender"] != "avatar"]
    avatar_messages = [msg for msg in messages if msg["sender"] == "avatar"]
    
    summary_text = f"Conversation between avatar and {conversation['participant_name']} with {len(messages)} total messages. "
    summary_text += f"Participant sent {len(participant_messages)} messages, avatar responded {len(avatar_messages)} times."
    
    key_points = [
        f"Conversation started at {conversation['started_at']}",
        f"Total messages exchanged: {len(messages)}",
        f"Participant: {conversation['participant_name']}",
        f"Avatar ID: {conversation['avatar_id']}"
    ]
    
    if messages:
        key_points.append(f"First message: {messages[0]['content'][:50]}...")
        key_points.append(f"Last message: {messages[-1]['content'][:50]}...")
    
    summary_obj = Summary(
        avatar_id=conversation["avatar_id"],
        conversation_id=conversation_id,
        summary_text=summary_text,
        key_points=key_points
    )
    
    await db.summaries.insert_one(summary_obj.dict())
    return summary_obj

@api_router.get("/summaries", response_model=List[Summary])
async def get_summaries(current_user: User = Depends(get_current_user), avatar_id: Optional[str] = None):
    query = {}
    if avatar_id:
        # Verify avatar belongs to current user
        avatar = await db.avatars.find_one({"id": avatar_id, "owner_id": current_user.id})
        if not avatar:
            raise HTTPException(status_code=404, detail="Avatar not found")
        query["avatar_id"] = avatar_id
    else:
        # Get all avatars belonging to current user
        user_avatars = await db.avatars.find({"owner_id": current_user.id}).to_list(1000)
        avatar_ids = [avatar["id"] for avatar in user_avatars]
        if avatar_ids:
            query["avatar_id"] = {"$in": avatar_ids}
        else:
            return []  # No avatars, no summaries
    
    summaries = await db.summaries.find(query).sort("generated_at", -1).to_list(1000)
    return [Summary(**summary) for summary in summaries]

@api_router.get("/summaries/{summary_id}", response_model=Summary)
async def get_summary(summary_id: str):
    summary = await db.summaries.find_one({"id": summary_id})
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return Summary(**summary)

@api_router.get("/avatars/{avatar_id}/summaries", response_model=List[Summary])
async def get_avatar_summaries(avatar_id: str):
    avatar = await db.avatars.find_one({"id": avatar_id})
    if not avatar:
        raise HTTPException(status_code=404, detail="Avatar not found")
    
    summaries = await db.summaries.find({"avatar_id": avatar_id}).sort("generated_at", -1).to_list(1000)
    return [Summary(**summary) for summary in summaries]

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("startup")
async def startup_event():
    await init_admin_user()

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

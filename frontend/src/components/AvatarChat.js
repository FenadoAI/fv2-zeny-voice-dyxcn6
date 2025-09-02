import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import { useParams, useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Badge } from './ui/badge';
import { ArrowLeft, Send, FileText, User, Bot } from 'lucide-react';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8001';
const API = `${API_BASE}/api`;

const AvatarChat = () => {
  const { avatarId } = useParams();
  const navigate = useNavigate();
  const [avatar, setAvatar] = useState(null);
  const [conversation, setConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [participantName, setParticipantName] = useState('');
  const [chatStarted, setChatStarted] = useState(false);
  const [summary, setSummary] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    fetchAvatar();
  }, [avatarId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchAvatar = async () => {
    try {
      const response = await axios.get(`${API}/avatars/${avatarId}`);
      setAvatar(response.data);
    } catch (error) {
      console.error('Error fetching avatar:', error);
    }
  };

  const startConversation = async () => {
    if (!participantName.trim()) return;
    
    try {
      const response = await axios.post(`${API}/conversations`, {
        avatar_id: avatarId,
        participant_name: participantName
      });
      setConversation(response.data);
      setChatStarted(true);
      
      // Add welcome message
      const welcomeMessage = {
        sender: 'avatar',
        content: `Hello ${participantName}! I'm ${avatar?.name}. ${avatar?.description} How can I help you today?`,
        timestamp: new Date().toISOString()
      };
      setMessages([welcomeMessage]);
    } catch (error) {
      console.error('Error starting conversation:', error);
    }
  };

  const sendMessage = async () => {
    if (!newMessage.trim() || !conversation) return;

    const message = {
      sender: participantName,
      content: newMessage
    };

    try {
      await axios.post(`${API}/conversations/${conversation.id}/messages`, message);
      
      // Fetch updated conversation to get all messages including AI response
      const updatedConv = await axios.get(`${API}/conversations/${conversation.id}`);
      setMessages(updatedConv.data.messages);
      setNewMessage('');
    } catch (error) {
      console.error('Error sending message:', error);
    }
  };

  const endConversation = async () => {
    if (!conversation) return;

    try {
      await axios.put(`${API}/conversations/${conversation.id}/end`);
      generateSummary();
    } catch (error) {
      console.error('Error ending conversation:', error);
    }
  };

  const generateSummary = async () => {
    if (!conversation) return;

    try {
      const response = await axios.post(`${API}/conversations/${conversation.id}/summary`);
      setSummary(response.data);
    } catch (error) {
      console.error('Error generating summary:', error);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (chatStarted) {
        sendMessage();
      } else {
        startConversation();
      }
    }
  };

  if (!avatar) {
    return <div className="flex justify-center items-center h-screen">Loading...</div>;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="max-w-4xl mx-auto p-6">
        {/* Header */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <Button 
              variant="outline" 
              onClick={() => navigate('/')}
              className="p-2"
            >
              <ArrowLeft className="w-4 h-4" />
            </Button>
            <Avatar className="h-12 w-12">
              <AvatarImage src={avatar.avatar_image} />
              <AvatarFallback>{avatar.name.charAt(0)}</AvatarFallback>
            </Avatar>
            <div>
              <h1 className="text-2xl font-bold">{avatar.name}</h1>
              <Badge variant="secondary">{avatar.personality}</Badge>
            </div>
          </div>
          {chatStarted && conversation && (
            <div className="space-x-2">
              <Button onClick={generateSummary} variant="outline">
                <FileText className="w-4 h-4 mr-2" />
                Generate Summary
              </Button>
              <Button onClick={endConversation} variant="destructive">
                End Chat
              </Button>
            </div>
          )}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Chat Interface */}
          <div className="lg:col-span-3">
            <Card className="h-[600px] flex flex-col">
              <CardHeader>
                <CardTitle>Chat with {avatar.name}</CardTitle>
              </CardHeader>
              <CardContent className="flex-1 flex flex-col">
                {!chatStarted ? (
                  <div className="flex-1 flex flex-col justify-center items-center space-y-4">
                    <div className="text-center">
                      <h3 className="text-lg font-semibold mb-2">Start a conversation</h3>
                      <p className="text-gray-600 mb-4">Enter your name to begin chatting with {avatar.name}</p>
                    </div>
                    <div className="w-full max-w-sm space-y-4">
                      <Input
                        placeholder="Your name"
                        value={participantName}
                        onChange={(e) => setParticipantName(e.target.value)}
                        onKeyPress={handleKeyPress}
                      />
                      <Button 
                        onClick={startConversation} 
                        className="w-full"
                        disabled={!participantName.trim()}
                      >
                        Start Chat
                      </Button>
                    </div>
                  </div>
                ) : (
                  <>
                    {/* Messages */}
                    <div className="flex-1 overflow-y-auto space-y-4 mb-4 p-4 bg-gray-50 rounded-lg">
                      {messages.map((message, index) => (
                        <div
                          key={index}
                          className={`flex items-start space-x-3 ${
                            message.sender === 'avatar' ? 'justify-start' : 'justify-end'
                          }`}
                        >
                          {message.sender === 'avatar' && (
                            <Avatar className="h-8 w-8">
                              <AvatarFallback><Bot className="w-4 h-4" /></AvatarFallback>
                            </Avatar>
                          )}
                          <div
                            className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                              message.sender === 'avatar'
                                ? 'bg-blue-500 text-white'
                                : 'bg-white border'
                            }`}
                          >
                            <p className="text-sm">{message.content}</p>
                            <p className="text-xs opacity-70 mt-1">
                              {new Date(message.timestamp).toLocaleTimeString()}
                            </p>
                          </div>
                          {message.sender !== 'avatar' && (
                            <Avatar className="h-8 w-8">
                              <AvatarFallback><User className="w-4 h-4" /></AvatarFallback>
                            </Avatar>
                          )}
                        </div>
                      ))}
                      <div ref={messagesEndRef} />
                    </div>

                    {/* Message Input */}
                    <div className="flex space-x-2">
                      <Input
                        placeholder="Type your message..."
                        value={newMessage}
                        onChange={(e) => setNewMessage(e.target.value)}
                        onKeyPress={handleKeyPress}
                        className="flex-1"
                      />
                      <Button onClick={sendMessage} disabled={!newMessage.trim()}>
                        <Send className="w-4 h-4" />
                      </Button>
                    </div>
                  </>
                )}
              </CardContent>
            </Card>
          </div>

          {/* Avatar Info & Summary */}
          <div className="space-y-6">
            {/* Avatar Details */}
            <Card>
              <CardHeader>
                <CardTitle>Avatar Details</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div>
                    <h4 className="font-semibold">Personality</h4>
                    <p className="text-sm text-gray-600">{avatar.personality}</p>
                  </div>
                  <div>
                    <h4 className="font-semibold">Description</h4>
                    <p className="text-sm text-gray-600">{avatar.description}</p>
                  </div>
                  {avatar.knowledge_base && (
                    <div>
                      <h4 className="font-semibold">Knowledge Base</h4>
                      <p className="text-sm text-gray-600">{avatar.knowledge_base}</p>
                    </div>
                  )}
                </div>
              </CardContent>
            </Card>

            {/* Summary */}
            {summary && (
              <Card>
                <CardHeader>
                  <CardTitle>Conversation Summary</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <p className="text-sm">{summary.summary_text}</p>
                    <div>
                      <h4 className="font-semibold text-sm">Key Points:</h4>
                      <ul className="text-xs text-gray-600 space-y-1 mt-1">
                        {summary.key_points.map((point, index) => (
                          <li key={index} className="flex items-start">
                            <span className="mr-2">•</span>
                            <span>{point}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default AvatarChat;
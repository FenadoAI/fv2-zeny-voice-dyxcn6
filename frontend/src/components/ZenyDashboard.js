import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Textarea } from './ui/textarea';
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogTrigger } from './ui/dialog';
import { Avatar, AvatarFallback, AvatarImage } from './ui/avatar';
import { Badge } from './ui/badge';
import { Plus, MessageCircle, TrendingUp, Users } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8001';
const API = `${API_BASE}/api`;

const ZenyDashboard = () => {
  const [avatars, setAvatars] = useState([]);
  const [summaries, setSummaries] = useState([]);
  const [showCreateDialog, setShowCreateDialog] = useState(false);
  const [newAvatar, setNewAvatar] = useState({
    name: '',
    personality: '',
    description: '',
    owner_id: 'user-123' // Mock user ID
  });
  const navigate = useNavigate();

  useEffect(() => {
    fetchAvatars();
    fetchSummaries();
  }, []);

  const fetchAvatars = async () => {
    try {
      const response = await axios.get(`${API}/avatars`);
      setAvatars(response.data);
    } catch (error) {
      console.error('Error fetching avatars:', error);
    }
  };

  const fetchSummaries = async () => {
    try {
      const response = await axios.get(`${API}/summaries`);
      setSummaries(response.data.slice(0, 5)); // Get latest 5 summaries
    } catch (error) {
      console.error('Error fetching summaries:', error);
    }
  };

  const createAvatar = async () => {
    try {
      await axios.post(`${API}/avatars`, newAvatar);
      setNewAvatar({ name: '', personality: '', description: '', owner_id: 'user-123' });
      setShowCreateDialog(false);
      fetchAvatars();
    } catch (error) {
      console.error('Error creating avatar:', error);
    }
  };

  const startChat = (avatarId) => {
    navigate(`/chat/${avatarId}`);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Zeny AI Dashboard</h1>
          <p className="text-gray-600 text-lg">Manage your AI avatars and monitor conversations</p>
        </div>

        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Active Avatars</CardTitle>
              <Users className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{avatars.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Total Conversations</CardTitle>
              <MessageCircle className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summaries.length}</div>
            </CardContent>
          </Card>
          <Card>
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-medium">Summaries Generated</CardTitle>
              <TrendingUp className="h-4 w-4 text-muted-foreground" />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold">{summaries.length}</div>
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Avatars Section */}
          <div className="lg:col-span-2">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-2xl font-semibold">Your Avatars</h2>
              <Dialog open={showCreateDialog} onOpenChange={setShowCreateDialog}>
                <DialogTrigger asChild>
                  <Button className="bg-blue-600 hover:bg-blue-700">
                    <Plus className="w-4 h-4 mr-2" />
                    Create Avatar
                  </Button>
                </DialogTrigger>
                <DialogContent className="sm:max-w-[425px]">
                  <DialogHeader>
                    <DialogTitle>Create New Avatar</DialogTitle>
                  </DialogHeader>
                  <div className="grid gap-4 py-4">
                    <Input
                      placeholder="Avatar Name"
                      value={newAvatar.name}
                      onChange={(e) => setNewAvatar({...newAvatar, name: e.target.value})}
                    />
                    <Input
                      placeholder="Personality (e.g., Friendly, Professional, Humorous)"
                      value={newAvatar.personality}
                      onChange={(e) => setNewAvatar({...newAvatar, personality: e.target.value})}
                    />
                    <Textarea
                      placeholder="Description"
                      value={newAvatar.description}
                      onChange={(e) => setNewAvatar({...newAvatar, description: e.target.value})}
                    />
                    <Button onClick={createAvatar} className="w-full">
                      Create Avatar
                    </Button>
                  </div>
                </DialogContent>
              </Dialog>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {avatars.map((avatar) => (
                <Card key={avatar.id} className="hover:shadow-lg transition-shadow">
                  <CardHeader>
                    <div className="flex items-center space-x-4">
                      <Avatar className="h-12 w-12">
                        <AvatarImage src={avatar.avatar_image} />
                        <AvatarFallback>{avatar.name.charAt(0)}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <CardTitle className="text-lg">{avatar.name}</CardTitle>
                        <Badge variant="secondary" className="mt-1">
                          {avatar.personality}
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <p className="text-gray-600 mb-4">{avatar.description}</p>
                    <Button 
                      onClick={() => startChat(avatar.id)}
                      className="w-full bg-green-600 hover:bg-green-700"
                    >
                      <MessageCircle className="w-4 h-4 mr-2" />
                      Start Chat
                    </Button>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>

          {/* Recent Summaries */}
          <div>
            <h2 className="text-2xl font-semibold mb-6">Recent Summaries</h2>
            <div className="space-y-4">
              {summaries.map((summary) => (
                <Card key={summary.id} className="hover:shadow-md transition-shadow">
                  <CardHeader className="pb-2">
                    <CardTitle className="text-sm">Summary #{summary.id.slice(-8)}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <p className="text-sm text-gray-600 mb-2">{summary.summary_text}</p>
                    <div className="text-xs text-gray-500">
                      {new Date(summary.generated_at).toLocaleDateString()}
                    </div>
                  </CardContent>
                </Card>
              ))}
              {summaries.length === 0 && (
                <Card>
                  <CardContent className="text-center py-8">
                    <p className="text-gray-500">No summaries yet</p>
                    <p className="text-sm text-gray-400">Start a conversation to generate summaries</p>
                  </CardContent>
                </Card>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ZenyDashboard;
import React, { useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Alert, AlertDescription } from './ui/alert';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/tabs';
import { LogIn, UserPlus, Settings } from 'lucide-react';

const API_BASE = process.env.REACT_APP_API_URL || 'http://localhost:8001';
const API = `${API_BASE}/api`;

const Login = ({ onLogin }) => {
  const [loginData, setLoginData] = useState({ username: '', password: '' });
  const [registerData, setRegisterData] = useState({ username: '', password: '', email: '' });
  const [adminData, setAdminData] = useState({ new_username: '', new_password: '' });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const [showAdminPanel, setShowAdminPanel] = useState(false);
  const [currentUser, setCurrentUser] = useState(null);

  const handleLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await axios.post(`${API}/auth/login`, loginData);
      const { access_token, user } = response.data;
      
      // Store token in localStorage
      localStorage.setItem('token', access_token);
      localStorage.setItem('user', JSON.stringify(user));
      
      // Set axios default header
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      setCurrentUser(user);
      onLogin(user, access_token);
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post(`${API}/auth/register`, registerData);
      setSuccess('Registration successful! Please login.');
      setRegisterData({ username: '', password: '', email: '' });
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  const handleQuickLogin = () => {
    setLoginData({ username: 'admin', password: 'admin' });
  };

  const handleAdminUpdate = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.put(`${API}/auth/admin/credentials`, adminData);
      setSuccess('Admin credentials updated successfully!');
      setAdminData({ new_username: '', new_password: '' });
      setShowAdminPanel(false);
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to update admin credentials');
    } finally {
      setLoading(false);
    }
  };

  const checkIfAdmin = async () => {
    try {
      const response = await axios.get(`${API}/auth/me`);
      if (response.data.is_admin) {
        setShowAdminPanel(true);
        setCurrentUser(response.data);
      } else {
        setError('Admin access required');
      }
    } catch (error) {
      setError('Please login first');
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-6">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Welcome to Zeny AI</h1>
          <p className="text-gray-600">Sign in to manage your AI avatars</p>
        </div>

        {!showAdminPanel ? (
          <Tabs defaultValue="login" className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="login">Login</TabsTrigger>
              <TabsTrigger value="register">Register</TabsTrigger>
            </TabsList>

            <TabsContent value="login">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <LogIn className="w-5 h-5 mr-2" />
                    Login
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleLogin} className="space-y-4">
                    <div>
                      <Label htmlFor="username">Username</Label>
                      <Input
                        id="username"
                        type="text"
                        placeholder="Enter username"
                        value={loginData.username}
                        onChange={(e) => setLoginData({...loginData, username: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="password">Password</Label>
                      <Input
                        id="password"
                        type="password"
                        placeholder="Enter password"
                        value={loginData.password}
                        onChange={(e) => setLoginData({...loginData, password: e.target.value})}
                        required
                      />
                    </div>
                    
                    {error && (
                      <Alert variant="destructive">
                        <AlertDescription>{error}</AlertDescription>
                      </Alert>
                    )}
                    
                    {success && (
                      <Alert className="border-green-200 bg-green-50">
                        <AlertDescription className="text-green-800">{success}</AlertDescription>
                      </Alert>
                    )}

                    <Button type="submit" className="w-full" disabled={loading}>
                      {loading ? 'Logging in...' : 'Login'}
                    </Button>
                    
                    <Button 
                      type="button" 
                      variant="outline" 
                      className="w-full" 
                      onClick={handleQuickLogin}
                    >
                      Quick Login (admin/admin)
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="register">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center">
                    <UserPlus className="w-5 h-5 mr-2" />
                    Register
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <form onSubmit={handleRegister} className="space-y-4">
                    <div>
                      <Label htmlFor="reg-username">Username</Label>
                      <Input
                        id="reg-username"
                        type="text"
                        placeholder="Choose username"
                        value={registerData.username}
                        onChange={(e) => setRegisterData({...registerData, username: e.target.value})}
                        required
                      />
                    </div>
                    <div>
                      <Label htmlFor="reg-email">Email (optional)</Label>
                      <Input
                        id="reg-email"
                        type="email"
                        placeholder="Enter email"
                        value={registerData.email}
                        onChange={(e) => setRegisterData({...registerData, email: e.target.value})}
                      />
                    </div>
                    <div>
                      <Label htmlFor="reg-password">Password</Label>
                      <Input
                        id="reg-password"
                        type="password"
                        placeholder="Choose password"
                        value={registerData.password}
                        onChange={(e) => setRegisterData({...registerData, password: e.target.value})}
                        required
                      />
                    </div>

                    <Button type="submit" className="w-full" disabled={loading}>
                      {loading ? 'Registering...' : 'Register'}
                    </Button>
                  </form>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        ) : (
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center">
                <Settings className="w-5 h-5 mr-2" />
                Admin Panel
              </CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleAdminUpdate} className="space-y-4">
                <div>
                  <Label htmlFor="new-username">New Admin Username</Label>
                  <Input
                    id="new-username"
                    type="text"
                    placeholder="New username"
                    value={adminData.new_username}
                    onChange={(e) => setAdminData({...adminData, new_username: e.target.value})}
                    required
                  />
                </div>
                <div>
                  <Label htmlFor="new-password">New Admin Password</Label>
                  <Input
                    id="new-password"
                    type="password"
                    placeholder="New password"
                    value={adminData.new_password}
                    onChange={(e) => setAdminData({...adminData, new_password: e.target.value})}
                    required
                  />
                </div>

                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? 'Updating...' : 'Update Admin Credentials'}
                </Button>
                
                <Button 
                  type="button" 
                  variant="outline" 
                  className="w-full" 
                  onClick={() => setShowAdminPanel(false)}
                >
                  Back
                </Button>
              </form>
            </CardContent>
          </Card>
        )}

        {!showAdminPanel && (
          <div className="mt-4 text-center">
            <Button 
              variant="link" 
              onClick={checkIfAdmin}
              className="text-sm text-gray-600"
            >
              Admin Settings
            </Button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Login;
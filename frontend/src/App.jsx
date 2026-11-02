import React, { useState, useEffect } from 'react';
import api from './services/api';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('token') || '');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [currentUser, setCurrentUser] = useState(null);

  // Data states
  const [employees, setEmployees] = useState([]);
  const [selectedEmployee, setSelectedEmployee] = useState(null);

  // Form states for creating an employee
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newUsername, setNewUsername] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [newRole, setNewRole] = useState('employee');
  const [newSalary, setNewSalary] = useState(50000);

  // PDF Report Generation States
  const [reportStatus, setReportStatus] = useState(''); // '', 'generating', 'success', 'error'
  const [pollInterval, setPollInterval] = useState(null);

  const [error, setError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // 1. Handle Login
  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);

    try {
      const response = await api.post('/api/auth/login', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });
      const accessToken = response.data.access_token;
      localStorage.setItem('token', accessToken);
      setToken(accessToken);
    } catch (err) {
      setError(err.response?.data?.detail || 'Login failed. Please check credentials.');
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('token');
    setToken('');
    setCurrentUser(null);
    setEmployees([]);
    setSelectedEmployee(null);
    if (pollInterval) clearInterval(pollInterval);
  };

  // Fetch current user details on token load
  useEffect(() => {
    if (token) {
      api.get('/api/employees/me')
        .then(res => setCurrentUser(res.data))
        .catch(() => handleLogout());
    }
  }, [token]);

  // Fetch all employees (list_all_employees)
  const fetchEmployees = async () => {
    if (currentUser && ['HR', 'MANAGER', 'ADMIN'].includes(currentUser?.role?.toUpperCase())) {
      try {
        const res = await api.get('/api/employees');
        // Handle both wrapped responses (res.data.data) and direct arrays (res.data)
        const employeeData = Array.isArray(res.data)
          ? res.data
          : (res.data.data || res.data.employees || []);
        setEmployees(employeeData);
      } catch (err) {
        console.error('Failed to fetch employee list', err);
      }
    }
  };

  // Fetch single employee by ID (get_employee_by_id)
  const handleViewDetails = async (id) => {
    try {
      console.log(`Fetching employee with ID: ${id}`);
      const res = await api.get(`/api/employees/${id}`);
      console.log("Single employee API response:", res.data);

      // Handle wrapped responses ({ success: true, data: {...} }) vs direct objects
      const empDetails = res.data.data || res.data.employee || res.data;
      setSelectedEmployee(empDetails);
    } catch (err) {
      console.error('Failed to fetch employee details error:', err);
      alert(`Failed to fetch employee details: ${err.response?.data?.message || err.message}`);
    }
  };

  useEffect(() => {
    fetchEmployees();
  }, [currentUser]);

  // 3. Create new employee (create_employee)
  const handleCreateEmployee = async (e) => {
    e.preventDefault();
    setError('');
    setSuccessMessage('');

    try {
      await api.post('/api/employees', {
        user_name: newUsername,
        user_password: newPassword,
        role: newRole,
        salary: parseFloat(newSalary)
      });
      setSuccessMessage('Employee created successfully!');
      setShowCreateModal(false);
      // Reset form with lowercase role default
      setNewUsername('');
      setNewPassword('');
      setNewRole('employee');
      setNewSalary(50000);
      // Refresh list
      fetchEmployees();
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create employee.');
    }
  };

  // 4. Trigger PDF Generation Background Task
  const handleGeneratePDF = async () => {
    setReportStatus('generating');
    try {
      const res = await api.post('/api/reports/generate-employee-pdf');
      const taskId = res.data.task_id;
      startPolling(taskId);
    } catch (err) {
      console.error('Failed to trigger PDF generation', err);
      setReportStatus('error');
    }
  };

  // 5. Poll Task Status Periodically
  const startPolling = (taskId) => {
    const interval = setInterval(async () => {
      try {
        const res = await api.get(`/api/reports/status/${taskId}`);
        if (res.data.ready) {
          clearInterval(interval);
          setPollInterval(null);
          if (res.data.status === 'SUCCESS' && res.data.download_url) {
            setReportStatus('success');
            triggerBrowserDownload(res.data.download_url, res.data.filename);
          } else {
            setReportStatus('error');
          }
        }
      } catch (err) {
        console.error('Error polling task status', err);
        clearInterval(interval);
        setPollInterval(null);
        setReportStatus('error');
      }
    }, 2000); // Poll every 2 seconds
    setPollInterval(interval);
  };

  // 6. Automatic Browser Download Trigger
  const triggerBrowserDownload = (url, filename) => {
    const link = document.createElement('a');
    link.target = '_blank'
    link.href = url;
    link.setAttribute('download', filename || 'employee_report.pdf');
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-slate-100 flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white rounded-xl shadow-lg p-8">
          <h2 className="text-2xl font-bold text-slate-800 text-center mb-6">Employee Portal Login</h2>
          {error && <div className="bg-red-50 text-red-600 p-3 rounded-lg mb-4 text-sm">{error}</div>}
          <form onSubmit={handleLogin} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                required
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none"
                required
              />
            </div>
            <button
              type="submit"
              className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 rounded-lg transition"
            >
              Sign In
            </button>
          </form>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-50">
      {/* Navigation Header */}
      <nav className="bg-white border-b px-8 py-4 flex justify-between items-center shadow-sm">
        <h1 className="text-xl font-bold text-slate-800">Enterprise Employee Portal</h1>
        <div className="flex items-center space-x-4">
          <span className="text-sm font-medium text-slate-600">
            Logged in as: <strong className="text-indigo-600">{currentUser?.user_name}</strong> ({currentUser?.role})
          </span>
          <button
            onClick={handleLogout}
            className="px-3 py-1.5 text-sm bg-slate-200 hover:bg-slate-300 rounded-md font-medium text-slate-700 transition"
          >
            Logout
          </button>
        </div>
      </nav>

      <main className="p-8 max-w-6xl mx-auto space-y-6">
        {successMessage && <div className="bg-emerald-50 text-emerald-700 p-4 rounded-xl border border-emerald-200">{successMessage}</div>}
        {error && <div className="bg-red-50 text-red-600 p-4 rounded-xl border border-red-200">{error}</div>}

        {/* My Profile Section */}
        <div className="bg-white p-6 rounded-xl shadow-sm border">
          <h2 className="text-lg font-semibold text-slate-800 mb-3">My Account Profile</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm text-slate-600">
            <div><strong>ID:</strong> {currentUser?.id}</div>
            <div><strong>Username:</strong> {currentUser?.user_name}</div>
            <div><strong>Role:</strong> <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded font-semibold">{currentUser?.role}</span></div>
            <div><strong>Salary:</strong> ${currentUser?.salary}</div>
          </div>
        </div>

        {/* Management Directory & Actions (Restricted via UI Role Check) */}
        {['HR', 'MANAGER', 'ADMIN'].includes(currentUser?.role?.toUpperCase()) && (
          <div className="bg-white p-6 rounded-xl shadow-sm border space-y-4">
            <div className="flex justify-between items-center">
              <h2 className="text-lg font-semibold text-slate-800">Employee Directory</h2>
              <div className="flex space-x-3">
                {/* PDF Report Download Button */}
                <button
                  onClick={handleGeneratePDF}
                  disabled={reportStatus === 'generating'}
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition shadow-sm text-white ${
                    reportStatus === 'generating'
                      ? 'bg-indigo-400 cursor-not-allowed'
                      : 'bg-emerald-600 hover:bg-emerald-700'
                  }`}
                >
                  {reportStatus === 'generating' ? 'Generating PDF...' : '📥 Download PDF Report'}
                </button>

                <button
                  onClick={() => setShowCreateModal(true)}
                  className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition shadow-sm"
                >
                  + Add New Employee
                </button>
              </div>
            </div>

            {reportStatus === 'success' && (
              <div className="text-sm text-emerald-600 font-medium bg-emerald-50 p-3 rounded-lg border border-emerald-200">
                ✓ PDF report generated and downloaded successfully!
              </div>
            )}
            {reportStatus === 'error' && (
              <div className="text-sm text-red-600 font-medium bg-red-50 p-3 rounded-lg border border-red-200">
                ✕ Failed to generate PDF report. Please try again.
              </div>
            )}

            {/* List All Employees Table */}
            <div className="overflow-x-auto">
              <table className="w-full text-left text-sm text-slate-600">
                <thead className="bg-slate-50 text-slate-700 uppercase text-xs">
                  <tr>
                    <th className="p-3">ID</th>
                    <th className="p-3">Username</th>
                    <th className="p-3">Role</th>
                    <th className="p-3">Salary</th>
                    <th className="p-3 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y">
                  {employees.map((emp) => (
                    <tr key={emp.id} className="hover:bg-slate-50 transition">
                      <td className="p-3 font-medium">{emp.id}</td>
                      <td className="p-3">{emp.user_name}</td>
                      <td className="p-3">
                        <span className="px-2 py-1 bg-slate-100 text-slate-700 rounded text-xs font-semibold">
                          {emp.role}
                        </span>
                      </td>
                      <td className="p-3">${emp.salary}</td>
                      <td className="p-3 text-right">
                        <button
                          onClick={() => handleViewDetails(emp.id)}
                          className="text-indigo-600 hover:text-indigo-800 font-medium text-xs bg-indigo-50 hover:bg-indigo-100 px-3 py-1.5 rounded transition"
                        >
                          View Details
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}
      </main>

      {/* Modal for Creating an Employee (POST /api/employees) */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-slate-800">Create New Employee</h3>
              <button onClick={() => setShowCreateModal(false)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>
            <form onSubmit={handleCreateEmployee} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Username</label>
                <input
                  type="text"
                  value={newUsername}
                  onChange={(e) => setNewUsername(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
                  required
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Password</label>
                <input
                  type="password"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
                  placeholder="At least 6 characters"
                  minLength={6}
                  required
                />
                <p className="text-xs text-slate-500 mt-1">Must be at least 6 characters long.</p>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Role</label>
                <select
                  value={newRole}
                  onChange={(e) => setNewRole(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm bg-white"
                >
                  <option value="employee">Employee</option>
                  <option value="developer">Developer</option>
                  <option value="hr">HR</option>
                  <option value="manager">Manager</option>
                  <option value="admin">Admin</option>
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-slate-700 mb-1">Salary ($)</label>
                <input
                  type="number"
                  value={newSalary}
                  onChange={(e) => setNewSalary(e.target.value)}
                  className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-indigo-500 outline-none text-sm"
                  required
                />
              </div>
              <div className="flex justify-end space-x-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="px-4 py-2 border rounded-lg text-sm font-medium text-slate-600 hover:bg-slate-50 transition"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-sm font-medium transition"
                >
                  Save Employee
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Modal for Viewing Employee by ID (GET /api/employees/{id}) */}
      {selectedEmployee && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-xl shadow-xl max-w-sm w-full p-6 space-y-4">
            <div className="flex justify-between items-center">
              <h3 className="text-lg font-bold text-slate-800">Employee Details</h3>
              <button onClick={() => setSelectedEmployee(null)} className="text-slate-400 hover:text-slate-600 font-bold">✕</button>
            </div>
            <div className="space-y-2 text-sm text-slate-600">
              <p><strong>ID:</strong> {selectedEmployee.id}</p>
              <p><strong>Username:</strong> {selectedEmployee.user_name}</p>
              <p><strong>Role:</strong> <span className="px-2 py-0.5 bg-indigo-50 text-indigo-700 rounded font-semibold">{selectedEmployee.role}</span></p>
              <p><strong>Salary:</strong> ${selectedEmployee.salary}</p>
            </div>
            <div className="pt-2 flex justify-end">
              <button
                onClick={() => setSelectedEmployee(null)}
                className="px-4 py-2 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg text-sm font-medium transition"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
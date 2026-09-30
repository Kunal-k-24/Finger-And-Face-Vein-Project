import { useEffect, useState } from 'react';
import { Users, ScanLine, Activity, Fingerprint, RefreshCcw } from 'lucide-react';
import { apiClient } from '../api/client';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

export const DashboardPage = () => {
  const [metrics, setMetrics] = useState<any>(null);
  const [logs, setLogs] = useState<any[]>([]);
  const [flRounds, setFlRounds] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [simulatingFl, setSimulatingFl] = useState(false);

  const fetchDashboardData = async () => {
    try {
      const [mRes, lRes, fRes] = await Promise.all([
        apiClient.get('/admin/metrics'),
        apiClient.get('/admin/logs?limit=10'),
        apiClient.get('/admin/federated')
      ]);
      setMetrics(mRes.data);
      setLogs(lRes.data);
      setFlRounds(fRes.data);
    } catch (err) {
      console.error("Failed to fetch dashboard data", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const triggerFlRound = async () => {
    setSimulatingFl(true);
    try {
      await apiClient.post('/federated/trigger_round');
      // Simulate delay then refresh
      setTimeout(() => {
        fetchDashboardData();
        setSimulatingFl(false);
      }, 2000);
    } catch (err) {
      console.error(err);
      setSimulatingFl(false);
    }
  };

  if (loading || !metrics) {
    return <div className="flex-1 flex items-center justify-center"><RefreshCcw className="animate-spin text-brand-500 h-8 w-8" /></div>;
  }

  return (
    <div className="flex-1 p-4 md:p-8 max-w-7xl mx-auto w-full">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-3xl font-bold text-white flex items-center gap-3">
            <Activity className="text-brand-500" />
            Admin Dashboard
          </h1>
          <p className="text-slate-400 mt-2">System metrics, authentication logs, and federated learning management.</p>
        </div>
        <button
          onClick={triggerFlRound}
          disabled={simulatingFl}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white rounded-lg font-medium flex items-center gap-2 transition-colors"
        >
          <RefreshCcw size={16} className={simulatingFl ? "animate-spin" : ""} />
          {simulatingFl ? "Training Round..." : "Trigger FL Round"}
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="glass-card p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-blue-500/20 rounded-lg text-blue-400"><Users size={24} /></div>
            <div>
              <p className="text-slate-400 text-sm font-medium">Total Users</p>
              <h3 className="text-2xl font-bold text-white">{metrics.total_users}</h3>
            </div>
          </div>
        </div>
        <div className="glass-card p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-indigo-500/20 rounded-lg text-indigo-400"><Fingerprint size={24} /></div>
            <div>
              <p className="text-slate-400 text-sm font-medium">Enrollments</p>
              <h3 className="text-2xl font-bold text-white">{metrics.total_enrollments}</h3>
            </div>
          </div>
        </div>
        <div className="glass-card p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-green-500/20 rounded-lg text-green-400"><ScanLine size={24} /></div>
            <div>
              <p className="text-slate-400 text-sm font-medium">Verifications</p>
              <h3 className="text-2xl font-bold text-white">{metrics.total_verifications}</h3>
            </div>
          </div>
        </div>
        <div className="glass-card p-6">
          <div className="flex items-center gap-4">
            <div className="p-3 bg-brand-500/20 rounded-lg text-brand-400"><Activity size={24} /></div>
            <div>
              <p className="text-slate-400 text-sm font-medium">Avg Latency</p>
              <h3 className="text-2xl font-bold text-white">{metrics.avg_latency_ms.toFixed(0)} ms</h3>
            </div>
          </div>
        </div>
      </div>

      <div className="grid lg:grid-cols-2 gap-8">
        <div className="glass-panel p-6">
          <h3 className="text-lg font-bold text-white mb-4">Recent Authentications</h3>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-sm text-slate-300">
              <thead className="bg-slate-800/50 text-slate-400">
                <tr>
                  <th className="px-4 py-3 rounded-tl-lg">Event</th>
                  <th className="px-4 py-3">Status</th>
                  <th className="px-4 py-3">Score</th>
                  <th className="px-4 py-3 rounded-tr-lg">Time</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/50">
                {logs.map((log) => (
                  <tr key={log.id} className="hover:bg-slate-800/30 transition-colors">
                    <td className="px-4 py-3 capitalize">{log.event_type}</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 text-xs font-medium rounded-full ${
                        log.status === 'success' ? 'bg-green-500/20 text-green-400' : 
                        log.status === 'rejected' ? 'bg-red-500/20 text-red-400' : 'bg-slate-500/20 text-slate-400'
                      }`}>
                        {log.status}
                      </span>
                    </td>
                    <td className="px-4 py-3 font-mono text-xs">{log.similarity_score ? (log.similarity_score * 100).toFixed(1) + '%' : '-'}</td>
                    <td className="px-4 py-3 text-xs text-slate-500">{new Date(log.timestamp).toLocaleString()}</td>
                  </tr>
                ))}
                {logs.length === 0 && (
                  <tr><td colSpan={4} className="px-4 py-8 text-center text-slate-500">No logs found</td></tr>
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="glass-panel p-6">
          <h3 className="text-lg font-bold text-white mb-4">FL Privacy Budget (Epsilon)</h3>
          {flRounds.length > 0 ? (
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={flRounds}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="round_number" stroke="#64748b" />
                  <YAxis stroke="#64748b" />
                  <Tooltip 
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.5rem' }} 
                    itemStyle={{ color: '#38acf8' }}
                  />
                  <Line type="monotone" dataKey="epsilon" stroke="#38acf8" strokeWidth={3} dot={{ fill: '#38acf8', r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-64 flex items-center justify-center text-slate-500">
              No federated rounds recorded yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

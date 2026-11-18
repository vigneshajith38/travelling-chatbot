import React, { useState } from 'react';
import { 
  PieChart, Pie, Cell, ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip, Legend 
} from 'recharts';
import { Wallet, Plus, Trash2, AlertTriangle, CheckCircle, TrendingUp, Users } from 'lucide-react';

const CATEGORY_COLORS = {
  Transportation: '#1b4332',
  Accommodation: '#2d6a4f',
  Food: '#d4a373',
  Activities: '#38bdf8',
  Shopping: '#b08968',
  'Emergency reserve': '#64748b',
  Miscellaneous: '#94a3b8'
};

export default function BudgetAnalytics({
  summary,
  expenses = [],
  onAddExpense,
  onDeleteExpense,
  currency = 'INR'
}) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [title, setTitle] = useState('');
  const [amount, setAmount] = useState('');
  const [category, setCategory] = useState('Food');
  const [payerName, setPayerName] = useState('Me');

  if (!summary) return null;

  const pieData = summary.categories
    .filter(c => c.spent > 0 || c.allocated > 0)
    .map(c => ({
      name: c.category,
      value: c.spent > 0 ? c.spent : c.allocated
    }));

  const comparisonData = summary.categories.map(c => ({
    name: c.category.slice(0, 8),
    Allocated: c.allocated,
    Spent: c.spent
  }));

  const handleCreateExpense = (e) => {
    e.preventDefault();
    if (!title.trim() || !amount) return;
    onAddExpense({
      title: title.trim(),
      amount: parseFloat(amount),
      category,
      payer_name: payerName.trim() || 'Me',
      currency,
      split_type: 'equal'
    });
    setTitle('');
    setAmount('');
    setShowAddForm(false);
  };

  return (
    <div className="space-y-6">
      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-4 rounded-2xl bg-white border border-sand-200 shadow-soft-sm">
          <span className="text-slate-500 text-xs font-medium block">Total Budget</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-bold font-serif text-slate-900">
              ₹{summary.total_budget?.toLocaleString()}
            </span>
            <span className="text-xs text-slate-400 font-semibold">{currency}</span>
          </div>
          <span className="text-[11px] text-slate-400 mt-1 block">
            ₹{summary.per_person_budget?.toLocaleString()} per person
          </span>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-sand-200 shadow-soft-sm">
          <span className="text-slate-500 text-xs font-medium block">Total Spent</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className="text-2xl font-bold font-serif text-forest-800">
              ₹{summary.total_actual_spent?.toLocaleString()}
            </span>
            <span className="text-xs text-slate-400 font-semibold">{currency}</span>
          </div>
          <div className="w-full bg-slate-100 rounded-full h-1.5 mt-2 overflow-hidden">
            <div 
              className={`h-full rounded-full transition-all ${
                summary.spending_percentage > 90 ? 'bg-rose-500' : 'bg-forest-600'
              }`}
              style={{ width: `${Math.min(100, summary.spending_percentage)}%` }}
            />
          </div>
        </div>

        <div className="p-4 rounded-2xl bg-white border border-sand-200 shadow-soft-sm">
          <span className="text-slate-500 text-xs font-medium block">Remaining Balance</span>
          <div className="flex items-baseline gap-1 mt-1">
            <span className={`text-2xl font-bold font-serif ${
              summary.remaining_budget < 0 ? 'text-rose-600' : 'text-emerald-700'
            }`}>
              ₹{summary.remaining_budget?.toLocaleString()}
            </span>
          </div>
          <span className="text-[11px] text-slate-500 mt-1 block">
            {summary.remaining_budget < 0 ? 'Over budget' : 'Available to spend'}
          </span>
        </div>

        <div className="p-4 rounded-2xl bg-forest-900 text-white shadow-soft-sm flex flex-col justify-between">
          <div>
            <span className="text-sand-300 text-xs font-semibold block">Expense Tracker</span>
            <p className="text-xs text-cream-200/80 mt-1">
              Logged {expenses.length} actual receipts and group shared expenses.
            </p>
          </div>
          <button
            onClick={() => setShowAddForm(true)}
            className="mt-3 w-full py-2 rounded-xl bg-sand-400 hover:bg-sand-300 text-forest-950 font-bold text-xs flex items-center justify-center gap-1.5 transition-colors"
          >
            <Plus className="w-4 h-4" />
            <span>Log Expense</span>
          </button>
        </div>
      </div>

      {/* Budget Alerts */}
      {summary.alerts?.length > 0 && (
        <div className="space-y-2">
          {summary.alerts.map((alert, idx) => (
            <div
              key={idx}
              className={`p-3.5 rounded-xl border flex items-center gap-2.5 text-xs ${
                alert.type === 'danger'
                  ? 'bg-rose-50 border-rose-200 text-rose-800'
                  : alert.type === 'warning'
                  ? 'bg-amber-50 border-amber-200 text-amber-800'
                  : 'bg-emerald-50 border-emerald-200 text-emerald-800'
              }`}
            >
              {alert.type === 'danger' ? (
                <AlertTriangle className="w-4 h-4 shrink-0 text-rose-600" />
              ) : (
                <CheckCircle className="w-4 h-4 shrink-0 text-emerald-600" />
              )}
              <span className="font-medium">{alert.message}</span>
            </div>
          ))}
        </div>
      )}

      {/* Visual Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Allocated vs Spent Bar Chart */}
        <div className="p-5 rounded-2xl bg-white border border-sand-200 shadow-soft-sm">
          <h4 className="font-serif font-bold text-slate-900 text-sm mb-4">
            Category Allocation vs. Actual Spending
          </h4>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={comparisonData}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip />
                <Legend wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }} />
                <Bar dataKey="Allocated" fill="#1b4332" radius={[4, 4, 0, 0]} />
                <Bar dataKey="Spent" fill="#d4a373" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Category Share Pie Chart */}
        <div className="p-5 rounded-2xl bg-white border border-sand-200 shadow-soft-sm flex flex-col justify-between">
          <h4 className="font-serif font-bold text-slate-900 text-sm mb-2">
            Budget Distribution Ratio
          </h4>
          <div className="h-56 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={55}
                  outerRadius={80}
                  paddingAngle={4}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={CATEGORY_COLORS[entry.name] || '#64748b'} 
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
          <div className="flex flex-wrap gap-2 justify-center text-[11px] text-slate-600 pt-2 border-t border-sand-100">
            {summary.categories.map((c) => (
              <div key={c.category} className="flex items-center gap-1.5">
                <span 
                  className="w-2.5 h-2.5 rounded-full" 
                  style={{ backgroundColor: CATEGORY_COLORS[c.category] || '#64748b' }}
                />
                <span>{c.category} ({c.percentage}%)</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Logged Expenses Table */}
      <div className="p-5 rounded-2xl bg-white border border-sand-200 shadow-soft-sm space-y-4">
        <div className="flex items-center justify-between">
          <h4 className="font-serif font-bold text-slate-900 text-sm">Itemized Expenses Log</h4>
          <button
            onClick={() => setShowAddForm(true)}
            className="px-3 py-1.5 rounded-lg bg-forest-800 hover:bg-forest-700 text-white font-semibold text-xs flex items-center gap-1 transition-colors"
          >
            <Plus className="w-3.5 h-3.5" />
            <span>Add Receipt</span>
          </button>
        </div>

        {showAddForm && (
          <form onSubmit={handleCreateExpense} className="p-4 rounded-xl bg-cream-50 border border-sand-300 space-y-3">
            <h5 className="font-bold text-xs text-slate-800">Add New Expense</h5>
            <div className="grid grid-cols-1 sm:grid-cols-4 gap-3 text-xs">
              <div>
                <label className="block text-[11px] font-medium text-slate-500 mb-1">Expense Description</label>
                <input
                  type="text"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  placeholder="e.g. Lunch at Heritage Spice Cafe"
                  className="w-full px-3 py-1.5 rounded-lg border border-sand-300 focus:ring-1 focus:ring-forest-600"
                  required
                />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-500 mb-1">Amount (₹)</label>
                <input
                  type="number"
                  value={amount}
                  onChange={(e) => setAmount(e.target.value)}
                  placeholder="650"
                  className="w-full px-3 py-1.5 rounded-lg border border-sand-300 focus:ring-1 focus:ring-forest-600"
                  required
                />
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-500 mb-1">Category</label>
                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="w-full px-3 py-1.5 rounded-lg border border-sand-300"
                >
                  <option value="Transportation">Transportation</option>
                  <option value="Accommodation">Accommodation</option>
                  <option value="Food">Food</option>
                  <option value="Activities">Activities</option>
                  <option value="Shopping">Shopping</option>
                  <option value="Miscellaneous">Miscellaneous</option>
                </select>
              </div>
              <div>
                <label className="block text-[11px] font-medium text-slate-500 mb-1">Paid By</label>
                <input
                  type="text"
                  value={payerName}
                  onChange={(e) => setPayerName(e.target.value)}
                  placeholder="Me / Rohan"
                  className="w-full px-3 py-1.5 rounded-lg border border-sand-300"
                />
              </div>
            </div>
            <div className="flex justify-end gap-2 pt-1">
              <button
                type="button"
                onClick={() => setShowAddForm(false)}
                className="px-3 py-1.5 rounded-lg text-slate-600 text-xs hover:bg-cream-200"
              >
                Cancel
              </button>
              <button
                type="submit"
                className="px-3.5 py-1.5 rounded-lg bg-forest-800 text-white font-semibold text-xs hover:bg-forest-700"
              >
                Save Expense
              </button>
            </div>
          </form>
        )}

        {expenses.length === 0 ? (
          <p className="text-xs text-slate-400 py-6 text-center italic">
            No expenses logged yet. Tap "Log Expense" to track receipts and split with friends.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-sand-200 text-slate-500 font-semibold">
                  <th className="py-2.5 px-3">Item</th>
                  <th className="py-2.5 px-3">Category</th>
                  <th className="py-2.5 px-3">Paid By</th>
                  <th className="py-2.5 px-3 text-right">Amount</th>
                  <th className="py-2.5 px-3 text-center">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-sand-100">
                {expenses.map((exp) => (
                  <tr key={exp.id} className="hover:bg-cream-50/70 transition-colors">
                    <td className="py-3 px-3 font-semibold text-slate-900">{exp.title}</td>
                    <td className="py-3 px-3">
                      <span className="px-2 py-0.5 rounded-full text-[10px] font-medium bg-sand-100 text-slate-700">
                        {exp.category}
                      </span>
                    </td>
                    <td className="py-3 px-3 text-slate-600">{exp.payer_name}</td>
                    <td className="py-3 px-3 text-right font-bold text-forest-800">
                      ₹{exp.amount?.toLocaleString()}
                    </td>
                    <td className="py-3 px-3 text-center">
                      <button
                        onClick={() => onDeleteExpense && onDeleteExpense(exp.id)}
                        className="text-slate-400 hover:text-rose-500 p-1 transition-colors"
                        title="Delete Expense"
                      >
                        <Trash2 className="w-3.5 h-3.5" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}


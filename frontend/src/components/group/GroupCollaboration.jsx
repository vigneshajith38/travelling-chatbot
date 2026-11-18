import React, { useState } from 'react';
import { 
  Users, UserPlus, ThumbsUp, ThumbsDown, MessageSquare, 
  Copy, Check, Share2, DollarSign, ArrowRight
} from 'lucide-react';

export default function GroupCollaboration({
  trip,
  members = [],
  votes = [],
  settlements = [],
  onInviteMember,
  onVote
}) {
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [inviteName, setInviteName] = useState('');
  const [inviteEmail, setInviteEmail] = useState('');
  const [copied, setCopied] = useState(false);
  const [voteComment, setVoteComment] = useState('');

  const handleCopyLink = () => {
    const inviteUrl = `${window.location.origin}/join/${trip?.share_code || 'WANDER26'}`;
    navigator.clipboard.writeText(inviteUrl);
    setCopied(true);
    setTimeout(() => setCopied(false), 2500);
  };

  const handleInvite = (e) => {
    e.preventDefault();
    if (!inviteName.trim() || !inviteEmail.trim()) return;
    onInviteMember({
      name: inviteName.trim(),
      email: inviteEmail.trim(),
      role: 'member'
    });
    setInviteName('');
    setInviteEmail('');
    setShowInviteModal(false);
  };

  return (
    <div className="space-y-6">
      {/* Group Trip Header Card */}
      <div className="p-6 rounded-2xl bg-gradient-to-r from-forest-900 to-forest-800 text-cream-100 shadow-soft-md flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-sand-300 font-semibold text-xs mb-1">
            <Users className="w-4 h-4" />
            <span>Collaborative Travel Hub</span>
          </div>
          <h3 className="font-serif font-bold text-xl text-white">
            {trip?.title} Group Expedition
          </h3>
          <p className="text-xs text-cream-300/80 mt-1 max-w-lg">
            Coordinate schedules, vote on preferred viewpoints and activities, and let WanderWise settle group bills automatically.
          </p>
        </div>

        <div className="flex items-center gap-2.5">
          <button
            onClick={handleCopyLink}
            className="px-3.5 py-2 rounded-xl bg-forest-700/80 hover:bg-forest-700 text-cream-100 text-xs font-semibold flex items-center gap-2 border border-sand-400/30 transition-all shadow-sm"
          >
            {copied ? <Check className="w-3.5 h-3.5 text-emerald-400" /> : <Copy className="w-3.5 h-3.5 text-sand-300" />}
            <span>{copied ? 'Invite Link Copied!' : 'Copy Invite Link'}</span>
          </button>
          <button
            onClick={() => setShowInviteModal(true)}
            className="px-3.5 py-2 rounded-xl bg-sand-400 hover:bg-sand-300 text-forest-950 text-xs font-bold flex items-center gap-1.5 transition-colors shadow-sm"
          >
            <UserPlus className="w-3.5 h-3.5" />
            <span>Invite Friend</span>
          </button>
        </div>
      </div>

      {/* Invite Member Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-sm flex items-center justify-center p-4">
          <div className="bg-white rounded-2xl p-6 max-w-md w-full shadow-2xl border border-sand-300 animate-in zoom-in-95 duration-150">
            <h4 className="font-serif font-bold text-base text-slate-900 mb-1">Invite Friend to Trip</h4>
            <p className="text-xs text-slate-500 mb-4">
              Send an invite so they can vote on itinerary activities and submit individual budgets.
            </p>
            <form onSubmit={handleInvite} className="space-y-3 text-xs">
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">Friend's Name</label>
                <input
                  type="text"
                  value={inviteName}
                  onChange={(e) => setInviteName(e.target.value)}
                  placeholder="e.g. Neha Patel"
                  className="w-full px-3.5 py-2 rounded-xl border border-sand-300 focus:ring-2 focus:ring-forest-600"
                  required
                />
              </div>
              <div>
                <label className="block text-[11px] font-semibold text-slate-700 mb-1">Email Address</label>
                <input
                  type="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="neha@example.com"
                  className="w-full px-3.5 py-2 rounded-xl border border-sand-300 focus:ring-2 focus:ring-forest-600"
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-3">
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="px-3.5 py-2 rounded-xl text-slate-600 hover:bg-cream-200"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 rounded-xl bg-forest-800 hover:bg-forest-700 text-white font-semibold"
                >
                  Send Invitation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Trip Members Grid */}
      <div className="p-5 rounded-2xl bg-white border border-sand-200 shadow-soft-sm">
        <h4 className="font-serif font-bold text-slate-900 text-sm mb-3">Group Members ({members.length})</h4>
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-3">
          {members.map((member) => (
            <div key={member.id} className="p-3.5 rounded-xl bg-cream-50/80 border border-sand-200 flex items-center gap-3">
              <div className="w-9 h-9 rounded-full bg-forest-800 text-sand-300 font-bold text-xs flex items-center justify-center shrink-0">
                {member.name.slice(0, 2).toUpperCase()}
              </div>
              <div className="overflow-hidden flex-1">
                <div className="flex items-center justify-between">
                  <h5 className="font-semibold text-xs text-slate-900 truncate">{member.name}</h5>
                  <span className="text-[10px] uppercase font-bold text-forest-700">
                    {member.role}
                  </span>
                </div>
                <p className="text-[11px] text-slate-500 truncate">{member.email}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Group Voting Section */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="p-5 rounded-2xl bg-white border border-sand-200 shadow-soft-sm space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-serif font-bold text-slate-900 text-sm">Activity & Spot Consensus Voting</h4>
            <span className="text-xs text-slate-500 font-medium">{votes.length} Votes Logged</span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            Vote on whether to keep or replace prospective activities. WanderWise surfaces recommendations with maximum group consensus.
          </p>

          <div className="space-y-3">
            {[
              { name: "Kolukkumalai Sunrise 4x4 Jeep Safari", type: "Activity", pros: 3, cons: 0 },
              { name: "Lockhart Orthodox Tea Tasting Lounge", type: "Activity", pros: 2, cons: 1 },
              { name: "Mirjan Basalt Fort Guided Walk", type: "Sight", pros: 2, cons: 0 }
            ].map((item, idx) => (
              <div key={idx} className="p-3 rounded-xl bg-cream-50 border border-sand-200 flex items-center justify-between gap-3">
                <div>
                  <h5 className="font-semibold text-xs text-slate-900">{item.name}</h5>
                  <span className="text-[10px] text-slate-500 font-medium">{item.type}</span>
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => onVote && onVote({ item_type: item.type, item_name: item.name, vote: 'up' })}
                    className="p-1.5 rounded-lg bg-emerald-50 hover:bg-emerald-100 text-emerald-700 flex items-center gap-1 text-[11px] font-bold border border-emerald-200 transition-colors"
                  >
                    <ThumbsUp className="w-3.5 h-3.5" />
                    <span>{item.pros}</span>
                  </button>
                  <button
                    onClick={() => onVote && onVote({ item_type: item.type, item_name: item.name, vote: 'down' })}
                    className="p-1.5 rounded-lg bg-rose-50 hover:bg-rose-100 text-rose-700 flex items-center gap-1 text-[11px] font-bold border border-rose-200 transition-colors"
                  >
                    <ThumbsDown className="w-3.5 h-3.5" />
                    <span>{item.cons}</span>
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Expense Splitting & Debt Settlements */}
        <div className="p-5 rounded-2xl bg-white border border-sand-200 shadow-soft-sm space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-serif font-bold text-slate-900 text-sm">Automated Expense Settlements</h4>
            <span className="text-[11px] text-forest-700 font-bold bg-forest-50 px-2 py-0.5 rounded-full">
              Fair Share Split
            </span>
          </div>
          <p className="text-xs text-slate-600 leading-relaxed">
            WanderWise calculates the fewest possible bank or UPI transfers to settle group food, cab, and hotel expenses.
          </p>

          {settlements?.settlements?.length > 0 ? (
            <div className="space-y-2.5">
              {settlements.settlements.map((s, idx) => (
                <div key={idx} className="p-3 rounded-xl bg-forest-50/70 border border-forest-200/80 flex items-center justify-between text-xs">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-slate-900">{s.from_member}</span>
                    <ArrowRight className="w-3.5 h-3.5 text-forest-700" />
                    <span className="font-bold text-slate-900">{s.to_member}</span>
                  </div>
                  <span className="font-serif font-extrabold text-forest-800 text-sm">
                    ₹{s.amount?.toLocaleString()}
                  </span>
                </div>
              ))}
            </div>
          ) : (
            <div className="p-6 rounded-xl bg-cream-50 border border-sand-200 text-center text-xs text-slate-500 italic">
              All group accounts are currently balanced or no expenses logged yet.
            </div>
          )}
        </div>
      </div>
    </div>
  );
}


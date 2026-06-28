export const LANGUAGES = [
  { code: 'en', label: 'English', nativeLabel: 'EN' },
  { code: 'hi', label: 'Hindi',   nativeLabel: 'हि' },
  { code: 'mr', label: 'Marathi', nativeLabel: 'म' },
]

export const DOMAIN_LABELS = {
  constitution:       { label: 'Constitution',       color: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/40 dark:text-indigo-300',  emoji: '🏛️' },
  criminal_law:       { label: 'Criminal Law',        color: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',             emoji: '⚖️' },
  criminal_procedure: { label: 'Criminal Procedure',  color: 'bg-orange-100 text-orange-800 dark:bg-orange-900/40 dark:text-orange-300', emoji: '🔍' },
  evidence:           { label: 'Evidence',            color: 'bg-amber-100 text-amber-800 dark:bg-amber-900/40 dark:text-amber-300',     emoji: '📋' },
  tenant_rights:      { label: 'Tenant Rights',       color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/40 dark:text-blue-300',         emoji: '🏠' },
  labor_law:          { label: 'Labour Law',          color: 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/40 dark:text-yellow-300', emoji: '⚒️' },
  domestic_violence:  { label: 'Domestic Violence',   color: 'bg-pink-100 text-pink-800 dark:bg-pink-900/40 dark:text-pink-300',         emoji: '🛡️' },
  rti:                { label: 'RTI',                 color: 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300',     emoji: '📜' },
  consumer_rights:    { label: 'Consumer Rights',     color: 'bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-300', emoji: '🛒' },
  police_misconduct:  { label: 'Police Misconduct',   color: 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-300',             emoji: '🚔' },
  property_dispute:   { label: 'Property Dispute',    color: 'bg-teal-100 text-teal-800 dark:bg-teal-900/40 dark:text-teal-300',         emoji: '🏗️' },
  family_law:         { label: 'Family Law',          color: 'bg-rose-100 text-rose-800 dark:bg-rose-900/40 dark:text-rose-300',         emoji: '👨‍👩‍👧' },
  motor_vehicles:     { label: 'Motor Vehicles',      color: 'bg-cyan-100 text-cyan-800 dark:bg-cyan-900/40 dark:text-cyan-300',         emoji: '🚗' },
  it_law:             { label: 'IT / Cyber Law',      color: 'bg-violet-100 text-violet-800 dark:bg-violet-900/40 dark:text-violet-300', emoji: '💻' },
  environmental:      { label: 'Environmental',       color: 'bg-lime-100 text-lime-800 dark:bg-lime-900/40 dark:text-lime-300',         emoji: '🌿' },
  general:            { label: 'General',             color: 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300',            emoji: '⚖️' },
}

export const EXAMPLE_QUERIES = {
  en: [
    'My landlord refuses to return my security deposit after I vacated',
    'My employer has not paid my salary for 2 months',
    'I want to file an RTI about a government scheme',
    'I bought a defective phone and company refuses refund',
  ],
  hi: [
    'मेरा मकान मालिक डिपॉजिट वापस नहीं कर रहा',
    'मेरे नियोक्ता ने 2 महीने से वेतन नहीं दिया',
    'मैं सरकारी योजना के लिए RTI दाखिल करना चाहता हूं',
  ],
  mr: [
    'माझा घरमालक डिपॉझिट परत देत नाही',
    'माझ्या मालकाने दोन महिने पगार दिला नाही',
  ],
}

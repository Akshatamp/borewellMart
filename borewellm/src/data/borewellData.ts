export interface ServiceItem {
  id: string;
  title: string;
  kicker: string;
  desc: string;
  specs: string[];
  priceStart: string;
  image: string;
}

export interface BrandPartner {
  name: string;
  category: string;
  rating: string;
  badge: string;
}

export interface Contractor {
  id: string;
  name: string;
  enterprise: string;
  state: string;
  city: string;
  rigType: string;
  compressor: string;
  rating: number;
  reviewsCount: number;
  experienceYears: number;
  completedWells: number;
  phone: string;
  verified: boolean;
  avatar: string;
  specialty: string;
  pricePerFt: number;
}

export const INDIAN_STATES = [
  'All States',
  'Karnataka',
  'Tamil Nadu',
  'Andhra Pradesh',
  'Telangana',
  'Maharashtra',
  'Gujarat',
  'Rajasthan',
  'Punjab'
];

export const CITIES_BY_STATE: Record<string, string[]> = {
  'All States': ['All Cities', 'Bengaluru', 'Coimbatore', 'Hyderabad', 'Chennai', 'Pune', 'Jaipur', 'Vijayawada', 'Ahmedabad'],
  'Karnataka': ['All Cities', 'Bengaluru', 'Mysuru', 'Hubballi', 'Tumakuru', 'Kolar', 'Mandya'],
  'Tamil Nadu': ['All Cities', 'Chennai', 'Coimbatore', 'Madurai', 'Salem', 'Tirupur', 'Erode'],
  'Andhra Pradesh': ['All Cities', 'Vijayawada', 'Visakhapatnam', 'Guntur', 'Tirupati', 'Anantapur'],
  'Telangana': ['All Cities', 'Hyderabad', 'Warangal', 'Karimnagar', 'Nizamabad', 'Mahbubnagar'],
  'Maharashtra': ['All Cities', 'Pune', 'Nashik', 'Nagpur', 'Aurangabad', 'Solapur', 'Kolhapur'],
  'Gujarat': ['All Cities', 'Ahmedabad', 'Rajkot', 'Surat', 'Vadodara', 'Mehsana'],
  'Rajasthan': ['All Cities', 'Jaipur', 'Jodhpur', 'Kota', 'Udaipur', 'Bikaner'],
  'Punjab': ['All Cities', 'Ludhiana', 'Amritsar', 'Jalandhar', 'Bathinda', 'Patiala']
};

export const CORE_SERVICES: ServiceItem[] = [
  {
    id: 'hydro-survey',
    title: 'Hydrogeological Survey & Groundwater Point Scanning',
    kicker: 'Precision Aquifer Mapping',
    desc: 'Advanced geo-resistivity sounding, vertical electrical sounding (VES), and satellite fracture trace analysis to pinpoint the highest water yield fracture zone before drilling.',
    specs: ['95%+ Strike Accuracy', 'Digital Resistivity Meter', 'Detailed Strata Report'],
    priceStart: '₹3,499 per point',
    image: 'https://images.unsplash.com/photo-1581092160607-ee22621dd758?auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 'hydraulic-drilling',
    title: 'High-Capacity Hydraulic Borewell Drilling (4.5" to 8.5")',
    kicker: 'Heavy DTH & Rotary Rigs',
    desc: 'Heavy-duty track & truck-mounted sensor rigs drilling down to 1,500 ft through hard Deccan trap granite, basalt, sandstone, and sedimentary formations.',
    specs: ['4.5" / 6.5" / 8.5" Diameter', 'Super-Silent Rigs', 'Class-V Heavy Casing'],
    priceStart: '₹95 / ft onwards',
    image: 'https://images.unsplash.com/photo-1504307651254-35680f356dfd?auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 'air-compressor-flushing',
    title: 'High-Pressure 1200 CFM Compressor Flushing & De-silting',
    kicker: 'Restoration & Re-activation',
    desc: 'Dual-stage 350-450 PSI high-pressure air flushing to clear choked mud, silt sediment, fine sand, and mineral crystallization to restore original water discharge.',
    specs: ['1200 CFM Air Blast', 'Slit & Clay Evacuation', 'Safe For Old Casings'],
    priceStart: '₹5,999 per well',
    image: 'https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 'submersible-pumps',
    title: 'Submersible Pump Installation & VFD Automation',
    kicker: 'Certified Motor Engineering',
    desc: 'Complete turnkey pumping setups with 100% copper rewindable water/oil-filled motors, anti-thrust bearings, digital dry-run protectors, and solar VFD drives.',
    specs: ['1.0 HP to 25.0 HP', 'HDPE / Column Pipe Fitting', 'ISI & BEE 5-Star Rated'],
    priceStart: '₹14,500 + installation',
    image: 'https://images.unsplash.com/photo-1581092335397-9583fe92d232?auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 'camera-scanning',
    title: 'Deep-Well 360° HD Dual-Lens Camera Inspection',
    kicker: 'Subterranean CCTV Diagnostics',
    desc: 'Waterproof downhole robotic camera with high-lumens LED rings scanning up to 1,500 ft to detect collapsed casings, stuck pumps, boulder entrapment, and live water veins.',
    specs: ['1080p Dual View Angle', 'Laser Depth Counter', 'USB Video Log Provided'],
    priceStart: '₹4,499 per scan',
    image: 'https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80'
  },
  {
    id: 'rainwater-recharge',
    title: 'Agricultural Artificial Recharge Shafts & V-Wire Filters',
    kicker: 'Aquifer Sustainability',
    desc: 'Government & CGWA compliant rainwater harvesting injection wells. Recharge depleting water tables using desilted gravel packs and multi-layer non-clogging V-wire screen filters.',
    specs: ['CGWA Guidelines Approved', 'Zero Silt Ingress', '5x Aquifer Life Boost'],
    priceStart: '₹18,000 complete kit',
    image: 'https://images.unsplash.com/photo-1500937386664-56d1dfef3854?auto=format&fit=crop&w=800&q=80'
  }
];

export const BRAND_PARTNERS: BrandPartner[] = [
  { name: 'Kirloskar Brothers', category: 'Heavy Agricultural Pumps', rating: '4.9/5', badge: 'Certified OEM' },
  { name: 'CRI Pumps', category: 'Deep-Well Submersibles', rating: '4.8/5', badge: 'Top Seller' },
  { name: 'Texmo Aqua', category: 'Stainless Steel Motors', rating: '4.9/5', badge: '5-Star Energy' },
  { name: 'Finolex Pipes', category: 'Class-V Column Pipes', rating: '4.8/5', badge: 'BIS 12818' },
  { name: 'Falcon Borewell', category: 'Patented Drop Pipes', rating: '4.7/5', badge: 'Torque-Proof' },
  { name: 'Ashirvad Pipes', category: 'Lead-Free Casing PVC', rating: '4.9/5', badge: 'NSF Certified' },
  { name: 'PRD Rigs', category: 'Heavy Hydraulic DTH', rating: '4.9/5', badge: 'Global Standard' },
  { name: 'Atlas Copco', category: 'High-Bar Compressors', rating: '5.0/5', badge: 'Industrial Heavy' }
];

export const CONTRACTORS: Contractor[] = [
  {
    id: 'c1',
    name: 'Suresh Gowda',
    enterprise: 'Shree Manjunatha Super Drillers',
    state: 'Karnataka',
    city: 'Bengaluru',
    rigType: 'PRD 450 Super Hydraulic Track Rig',
    compressor: 'Atlas Copco 1200 CFM / 350 PSI',
    rating: 4.9,
    reviewsCount: 342,
    experienceYears: 18,
    completedWells: 2850,
    phone: '+91 84317 38810',
    verified: true,
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=200&q=80',
    specialty: 'Deep Granitic Rock (up to 1,400 ft)',
    pricePerFt: 98
  },
  {
    id: 'c2',
    name: 'P. Murugan',
    enterprise: 'Kaveri Groundwater & Rig Services',
    state: 'Tamil Nadu',
    city: 'Coimbatore',
    rigType: 'KLR 650 Truck Rig with Robotic Arm',
    compressor: 'Elgi 1100 CFM Twin Turbo',
    rating: 4.95,
    reviewsCount: 418,
    experienceYears: 22,
    completedWells: 3400,
    phone: '+91 84317 38810',
    verified: true,
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=200&q=80',
    specialty: 'High-Yield Agricultural Irrigation & Farms',
    pricePerFt: 92
  },
  {
    id: 'c3',
    name: 'K. Venkat Reddy',
    enterprise: 'Balaji Heavy Hydro Solutions',
    state: 'Telangana',
    city: 'Hyderabad',
    rigType: 'Schramm Style Rotary & DTH Combo',
    compressor: 'Ingersoll Rand 1250 CFM 400 PSI',
    rating: 4.85,
    reviewsCount: 290,
    experienceYears: 15,
    completedWells: 2100,
    phone: '+91 84317 38810',
    verified: true,
    avatar: 'https://images.unsplash.com/photo-1472099645785-5658abf4ff4e?auto=format&fit=crop&w=200&q=80',
    specialty: 'Urban Compact & Residential Deep Borewells',
    pricePerFt: 105
  },
  {
    id: 'c4',
    name: 'Dilip Patel',
    enterprise: 'Sardar Hydro Geotech Drillers',
    state: 'Gujarat',
    city: 'Ahmedabad',
    rigType: 'Crawler Mounted Reverse Circulation Rig',
    compressor: 'Chicago Pneumatic 1150 CFM',
    rating: 4.88,
    reviewsCount: 312,
    experienceYears: 19,
    completedWells: 2600,
    phone: '+91 84317 38810',
    verified: true,
    avatar: 'https://images.unsplash.com/photo-1519085360753-af0119f7cbe7?auto=format&fit=crop&w=200&q=80',
    specialty: 'Alluvial Sand Formations & Gravel Packing',
    pricePerFt: 88
  },
  {
    id: 'c5',
    name: 'Ravinder Singh',
    enterprise: 'Khalsa Deep Borewell Corp',
    state: 'Punjab',
    city: 'Ludhiana',
    rigType: 'PRD Multi-Purpose Tractor & Truck Rigs',
    compressor: 'Atlas Copco 1300 CFM High Flow',
    rating: 4.92,
    reviewsCount: 265,
    experienceYears: 24,
    completedWells: 3900,
    phone: '+91 84317 38810',
    verified: true,
    avatar: 'https://images.unsplash.com/photo-1506794778202-cad84cf45f1d?auto=format&fit=crop&w=200&q=80',
    specialty: 'Tubewell Deep Recharging & Paddy Irrigation',
    pricePerFt: 90
  },
  {
    id: 'c6',
    name: 'Ganesh Deshmukh',
    enterprise: 'Sahyadri Agro-Water Engineers',
    state: 'Maharashtra',
    city: 'Pune',
    rigType: 'DTH Sensor Rig 4.5" & 6.5"',
    compressor: 'Elgi Horizon 1200 CFM',
    rating: 4.87,
    reviewsCount: 215,
    experienceYears: 16,
    completedWells: 1950,
    phone: '+91 84317 38810',
    verified: true,
    avatar: 'https://images.unsplash.com/photo-1522075469751-3a6694fb2f61?auto=format&fit=crop&w=200&q=80',
    specialty: 'Black Cotton Soil & Basalt Hard Layer',
    pricePerFt: 100
  }
];

export const VENDOR_PLAN = {
  title: 'GoogleBore Verified Rig Contractor Listing',
  originalPrice: 10000,
  offerPrice: 999,
  duration: '6 Months Full Access',
  guarantee: 'Guaranteed 25+ Verified High-Intent Customer Inquiries',
  features: [
    'Google Business Profile (GBP) & Map Pin Optimization for Drillers',
    'Direct Customer Phone Call Leads sent straight to your mobile',
    'Verified Contractor Badge on GoogleBore.com & BorewellMart',
    'Customer Depth Calculator Lead routing for your taluk/district',
    'Submersible pump & pipe dealer discount tie-ups (Save up to 15%)',
    'Instant WhatsApp booking notifications & CRM lead manager'
  ]
};

export const GEOLOGICAL_STRATA = [
  {
    depthMin: 0,
    depthMax: 80,
    name: 'Topsoil & Weathered Regolith',
    description: 'Soft clay, silt, loose pebbles. Protected by Schedule-40 / Class-V heavy PVC or GI surface casing pipe to stop cave-ins.',
    color: '#8b5a2b',
    texture: 'repeating-linear-gradient(45deg, #a06b3a, #a06b3a 10px, #8d5c2e 10px, #8d5c2e 20px)',
    waterLikelihood: 'Very Low (Surface Runoff)',
    casingRequired: 'Compulsory GI/PVC Casing'
  },
  {
    depthMin: 80,
    depthMax: 260,
    name: 'Fractured Semi-Weathered Rock Zone',
    description: 'Decomposed granite, fissured schist, and fractured basalt layers. Drilling with DTH button bit begins.',
    color: '#5c6479',
    texture: 'repeating-linear-gradient(60deg, #626c84, #626c84 12px, #525a70 12px, #525a70 24px)',
    waterLikelihood: 'Moderate (Minor 0.5 - 1.0 inch seepage)',
    casingRequired: 'Optional inner liner if collapsed'
  },
  {
    depthMin: 260,
    depthMax: 500,
    name: 'Hard Crystalline Bedrock (Granite/Basalt)',
    description: 'Dense mass requiring high-pressure pneumatic hammer (350+ PSI) and tungsten carbide button drill bits.',
    color: '#343c4f',
    texture: 'repeating-linear-gradient(30deg, #3d465c, #3d465c 15px, #2a3142 15px, #2a3142 30px)',
    waterLikelihood: 'Moderate to High in primary joint fissures',
    casingRequired: 'Bare rock self-supporting bore'
  },
  {
    depthMin: 500,
    depthMax: 1200,
    name: 'Deep Aquifer & High-Pressure Water Cavity',
    description: 'Confined deep regional aquifer fissures under intense hydrostatic pressure. High volume discharge (2.5" to 4.5" water source).',
    color: '#0d4a75',
    texture: 'repeating-linear-gradient(15deg, #0b4975, #0b4975 14px, #073556 14px, #073556 28px)',
    waterLikelihood: 'MAXIMUM YIELD (2,500 - 6,000+ Litres/Hour)',
    casingRequired: 'V-Wire screen recommended for sandy veins'
  }
];

export const FAQS = [
  {
    q: 'How is the borewell drilling cost calculated?',
    a: 'Total cost comprises: 1) Rig mobilization & setup charge, 2) Per-foot drilling rate (ranges ₹85 - ₹120/ft based on rock hardness), 3) Casing pipe cost (PVC Class-V or GI) for the top soil depth, 4) High-pressure compressor flushing, and 5) Submersible motor and column pipe accessories.'
  },
  {
    q: 'Why is hydrogeological ground survey essential before drilling?',
    a: 'A scientific geo-resistivity survey analyzes subsurface electrical resistivity anomalies to pinpoint natural fractures and aquifers. It eliminates random blind drilling and boosts strike success rates up to 95%.'
  },
  {
    q: 'What diameter borewell should I choose: 4.5" vs 6.5"?',
    a: 'For domestic residences, 4.5" or 6.0" is standard and accommodates 3" to 4" submersible pumps. For large agricultural farms, orchards, commercial industries, and high-yield borewells, 6.5" is strongly recommended to house high-stage 5 HP - 15 HP pumps.'
  },
  {
    q: 'How does GoogleBore verify drilling rig contractors?',
    a: 'Every listed contractor undergoes physical inspection of rig machinery (DTH capacity, compressor CFM rating), verification of GST & trade licenses, past customer reviews, and agreement to fixed transparent per-foot pricing.'
  }
];

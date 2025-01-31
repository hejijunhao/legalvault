// src/types/paralegal.ts

export interface VPProfile {
  name: string;
  email: string;
  level: number;
  avatar: string;
}

export interface VPAbility {
  id: string;
  name: string;
  description: string;
  icon: string;
  status: 'active' | 'locked' | 'available';
}

export interface VPBehavior {
  id: string;
  name: string;
  icon: string;
  color: string;
}

export interface VPKnowledge {
  level: number;
  progress: number;
  areas: Array<{
    name: string;
    level: number;
    icon: string;
  }>;
}

export interface VPAccess {
  id: string;
  name: string;
  icon: string;
  status: 'granted' | 'pending' | 'revoked';
}

export interface VPState {
  profile: VPProfile;
  abilities: VPAbility[];
  behaviors: VPBehavior[];
  knowledge: VPKnowledge;
  access: VPAccess[];
}
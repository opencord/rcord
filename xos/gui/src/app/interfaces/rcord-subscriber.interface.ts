
export interface IRCordSubscriber {
  id: string;
  service_specific_attribute: any; // stringified JSON
}

export interface IRCordSubscriberDevice {
  name: string;
  mac: string;
  level: string;
}
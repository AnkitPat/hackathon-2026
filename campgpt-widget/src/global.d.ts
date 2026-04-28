export {};

declare global {
  interface Window {
    MyChatbot: {
      init: (config: any) => void;
      setData: (data: any) => void;
    };
  }
}
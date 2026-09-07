import { ChevronRight } from "lucide-react";

export default function Hero() {
  return (
    <div className="flex flex-col items-center text-center pt-24 pb-16 px-4">
      <div className="relative group cursor-default">
        {/* Neon glow effect behind the text */}
        <div className="absolute -inset-1 blur-2xl opacity-20 bg-matrix group-hover:opacity-40 transition-opacity duration-1000 rounded-full" />
        
        <h1 className="relative text-5xl sm:text-7xl font-bold tracking-tighter text-foreground mb-4 animate-glitch hover:animate-flicker">
          <span className="text-matrix drop-shadow-[0_0_15px_rgba(0,255,65,0.8)]">Stega</span>
          Guard
        </h1>
      </div>
      
      <p className="max-w-xl text-lg text-dim font-mono mb-10">
        Advanced steganographic payload & backdoor detection for deep learning model weights.
      </p>
      
      {/* We will leave out the "Begin Scan" button if the upload zone itself is the action, 
          or we can render a button that smooth scrolls to the upload zone */}
      <button 
        onClick={() => document.getElementById('upload-zone')?.scrollIntoView({ behavior: 'smooth' })}
        className="group relative inline-flex items-center gap-2 overflow-hidden rounded-sm bg-matrix px-8 py-3 text-sm font-bold uppercase tracking-widest text-background transition-all hover:bg-matrix/90 focus:outline-none focus:ring-2 focus:ring-matrix focus:ring-offset-2 focus:ring-offset-background"
      >
        <span className="absolute inset-0 bg-[linear-gradient(90deg,transparent_0%,rgba(255,255,255,0.3)_50%,transparent_100%)] w-[200%] -translate-x-[150%] animate-[scanline_2s_linear_infinite]" />
        Begin Scan
        <ChevronRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
      </button>
    </div>
  );
}

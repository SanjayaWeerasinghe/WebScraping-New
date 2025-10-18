import { Button } from "@/components/ui/button";
import { Link } from "react-router-dom";
import { ArrowRight, Database, TrendingUp, Palette } from "lucide-react";
import heroBg from "@/assets/hero-bg.jpg";

const Home = () => {
  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden">
        <div 
          className="absolute inset-0 opacity-30"
          style={{ 
            backgroundImage: `url(${heroBg})`,
            backgroundSize: 'cover',
            backgroundPosition: 'center'
          }}
        />
        <div className="absolute inset-0 bg-gradient-primary opacity-60" />
        
        <div className="container relative mx-auto px-4 py-32">
          <div className="max-w-4xl mx-auto text-center space-y-8">
            <h1 className="text-5xl md:text-6xl font-bold text-primary-foreground leading-tight">
              Transform Web Data into
              <span className="block bg-gradient-to-r from-accent-glow to-primary-glow bg-clip-text text-transparent">
                Competitive Intelligence
              </span>
            </h1>
            
            <p className="text-xl text-primary-foreground/90 max-w-2xl mx-auto leading-relaxed">
              ScrapeVision is your comprehensive platform for automated competitor analysis. 
              Track pricing trends, analyze color preferences, and gain market insights in real-time.
            </p>
            
            <div className="flex gap-4 justify-center pt-6">
              <Link to="/scraping">
                <Button size="lg" variant="secondary" className="gap-2 shadow-lg hover:shadow-xl transition-all">
                  Start Exploring
                  <ArrowRight className="w-5 h-5" />
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="py-24 bg-gradient-subtle">
        <div className="container mx-auto px-4">
          <h2 className="text-3xl md:text-4xl font-bold text-center mb-16">
            Powerful Analytics at Your Fingertips
          </h2>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            <div className="bg-card p-8 rounded-2xl border border-border shadow-lg hover:shadow-xl transition-all">
              <div className="w-12 h-12 rounded-lg bg-primary/10 flex items-center justify-center mb-6">
                <Database className="w-6 h-6 text-primary" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Web Scraping</h3>
              <p className="text-muted-foreground leading-relaxed">
                Automatically collect and organize competitor product data. Filter by brand, type, and category for precise analysis.
              </p>
            </div>

            <div className="bg-card p-8 rounded-2xl border border-border shadow-lg hover:shadow-xl transition-all">
              <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center mb-6">
                <TrendingUp className="w-6 h-6 text-accent" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Price Analysis</h3>
              <p className="text-muted-foreground leading-relaxed">
                Visualize pricing strategies across competitors. Identify opportunities and track market positioning with interactive charts.
              </p>
            </div>

            <div className="bg-card p-8 rounded-2xl border border-border shadow-lg hover:shadow-xl transition-all">
              <div className="w-12 h-12 rounded-lg bg-success/10 flex items-center justify-center mb-6">
                <Palette className="w-6 h-6 text-success" />
              </div>
              <h3 className="text-xl font-semibold mb-3">Color Trends</h3>
              <p className="text-muted-foreground leading-relaxed">
                Discover trending colors in the market. Understand consumer preferences and optimize your product offerings.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-24">
        <div className="container mx-auto px-4">
          <div className="max-w-3xl mx-auto text-center space-y-6 bg-card p-12 rounded-2xl border border-border shadow-lg">
            <h2 className="text-3xl md:text-4xl font-bold">
              Ready to gain market insights?
            </h2>
            <p className="text-lg text-muted-foreground">
              Start analyzing competitor data and make informed business decisions today.
            </p>
            <Link to="/scraping">
              <Button size="lg" className="gap-2 shadow-md">
                View Scraped Data
                <ArrowRight className="w-5 h-5" />
              </Button>
            </Link>
          </div>
        </div>
      </section>
    </div>
  );
};

export default Home;

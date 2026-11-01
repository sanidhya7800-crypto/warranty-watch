import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Sidebar, ScreenId } from './components/Sidebar';
import { Header } from './components/Header';
import { DashboardView } from './views/DashboardView';
import { ProductsView } from './views/ProductsView';
import { AddProductView } from './views/AddProductView';
import { ProductDetailView } from './views/ProductDetailView';
import { WarrantyIntelligenceView } from './views/WarrantyIntelligenceView';
import { AIAssistantView } from './views/AIAssistantView';
import { ServiceRequestsView } from './views/ServiceRequestsView';
import { RecallsView } from './views/RecallsView';
import { ActivityView } from './views/ActivityView';
import { SettingsView } from './views/SettingsView';

import { 
  Product, 
  ServiceRequest, 
  RecallAlert, 
  NotificationItem, 
  TinyFishActivity, 
  DashboardMetrics, 
  KeyStatus 
} from './types';

import { 
  getDashboard, 
  getProducts, 
  getServiceRequests, 
  getRecalls, 
  getNotifications, 
  getActivity, 
  getSettings, 
  getCategories, 
  getStatuses,
  updateMode
} from './api';

export const App: React.FC = () => {
  const [currentScreen, setCurrentScreen] = useState<ScreenId>('dashboard');
  const [selectedProductId, setSelectedProductId] = useState<number | null>(null);

  const [dashboardMetrics, setDashboardMetrics] = useState<DashboardMetrics | null>(null);
  const [products, setProducts] = useState<Product[]>([]);
  const [requests, setRequests] = useState<ServiceRequest[]>([]);
  const [recalls, setRecalls] = useState<RecallAlert[]>([]);
  const [notifications, setNotifications] = useState<NotificationItem[]>([]);
  const [activities, setActivities] = useState<TinyFishActivity[]>([]);
  const [keyStatus, setKeyStatus] = useState<KeyStatus | null>(null);
  const [categories, setCategories] = useState<string[]>([]);
  const [statuses, setStatuses] = useState<string[]>([
    'Draft', 'Submitted', 'Pending', 'Technician Assigned', 'In Progress', 'Resolved', 'Rejected'
  ]);

  const [loading, setLoading] = useState(false);

  // Derived selected product - 100% stable, cannot fluctuate from stale callbacks or re-renders
  const selectedProduct = useMemo(() => {
    if (selectedProductId !== null) {
      const found = products.find((p) => p.id === selectedProductId);
      if (found) return found;
    }
    return products.length > 0 ? products[0] : null;
  }, [products, selectedProductId]);

  const refreshAllData = useCallback(async () => {
    setLoading(true);
    try {
      const [
        dashRes,
        prodRes,
        srRes,
        recRes,
        notifRes,
        actRes,
        settRes,
        catRes,
        statRes,
      ] = await Promise.allSettled([
        getDashboard(),
        getProducts(),
        getServiceRequests(),
        getRecalls(),
        getNotifications(),
        getActivity(),
        getSettings(),
        getCategories(),
        getStatuses(),
      ]);

      if (dashRes.status === 'fulfilled') setDashboardMetrics(dashRes.value.data);
      if (prodRes.status === 'fulfilled') {
        const prodList = prodRes.value.data;
        setProducts(prodList);
        setSelectedProductId((prevId) => {
          // If user already selected a product that exists in list, retain it!
          if (prevId !== null && prodList.some((p) => p.id === prevId)) {
            return prevId;
          }
          // Only default to first product if nothing was selected yet
          return prodList.length > 0 ? prodList[0].id : null;
        });
      }
      if (srRes.status === 'fulfilled') setRequests(srRes.value.data);
      if (recRes.status === 'fulfilled') setRecalls(recRes.value.data);
      if (notifRes.status === 'fulfilled') setNotifications(notifRes.value.data);
      if (actRes.status === 'fulfilled') setActivities(actRes.value.data);
      if (settRes.status === 'fulfilled') setKeyStatus(settRes.value.data);
      if (catRes.status === 'fulfilled') setCategories(catRes.value.data);
      if (statRes.status === 'fulfilled') setStatuses(statRes.value.data);
    } catch (err) {
      console.error('Failed to refresh data', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    refreshAllData();
  }, [refreshAllData]);

  const handleToggleMode = async (newMode: 'live' | 'demo') => {
    try {
      await updateMode(newMode);
      await refreshAllData();
    } catch (err) {
      console.error(err);
      alert('Failed to switch mode.');
    }
  };

  const getScreenTitle = () => {
    switch (currentScreen) {
      case 'dashboard':
        return { title: 'Appliance Intelligence Dashboard', sub: 'Holistic view of warranty status, upcoming expiries and background monitors' };
      case 'products':
        return { title: 'My Appliances & Electronics', sub: 'Manage registered devices, proof of purchase invoices and active coverage' };
      case 'add-product':
        return { title: 'Register New Appliance', sub: 'Add a home appliance, warranty duration, and invoice documentation' };
      case 'product-detail':
        return { title: 'Appliance Intelligence Sheet', sub: selectedProduct ? `${selectedProduct.manufacturer} ${selectedProduct.model_number}` : 'Appliance details' };
      case 'warranty':
        return { title: 'Warranty Intelligence Engine', sub: 'TinyFish Search & Fetch pipeline for official manufacturer policies' };
      case 'assistant':
        return { title: 'AI Service Troubleshooter', sub: 'Multi-step autonomous issue investigation powered by TinyFish Agent' };
      case 'service-requests':
        return { title: 'Service Requests & Repair Portal', sub: 'OEM repair tracker and remote TinyFish Browser support portal sessions' };
      case 'recalls':
        return { title: 'Recall Alerts & Safety Notices', sub: 'Proactive detection of manufacturer notices via TinyFish Search' };
      case 'activity':
        return { title: 'TinyFish Activity Audit Trail', sub: 'Real-time telemetry and JSON provenance for all 5 capabilities' };
      case 'settings':
        return { title: 'Platform Settings & Cloud Monitors', sub: 'TinyFish Monitor management, SDK credentials status, and Live/Demo mode' };
      default:
        return { title: 'Warranty Watch', sub: 'After-sales intelligence' };
    }
  };

  const { title, sub } = getScreenTitle();

  return (
    <div className="flex min-h-screen bg-[#090d16] text-slate-100 selection:bg-indigo-500 selection:text-white">
      {/* Sidebar */}
      <Sidebar
        currentScreen={currentScreen}
        onNavigate={(screen) => setCurrentScreen(screen)}
        mode={keyStatus?.mode || 'live'}
        keyPresent={keyStatus?.key_present || false}
        selectedProductName={selectedProduct?.name}
      />

      {/* Main Content Pane */}
      <div className="flex-1 flex flex-col min-w-0 overflow-y-auto h-screen">
        <Header
          title={title}
          subtitle={sub}
          mode={keyStatus?.mode || 'live'}
          onToggleMode={handleToggleMode}
          notifications={notifications}
          onRefreshData={refreshAllData}
          loading={loading}
        />

        <main className="flex-1 pb-16">
          {currentScreen === 'dashboard' && (
            <DashboardView
              metrics={dashboardMetrics}
              onNavigate={(s) => setCurrentScreen(s)}
              onSelectProduct={(p) => setSelectedProductId(p.id)}
            />
          )}

          {currentScreen === 'products' && (
            <ProductsView
              products={products}
              categories={categories}
              onSelectProduct={(p) => setSelectedProductId(p.id)}
              onNavigate={(s) => setCurrentScreen(s)}
              onRefresh={refreshAllData}
            />
          )}

          {currentScreen === 'add-product' && (
            <AddProductView
              categories={categories}
              onNavigate={(s) => setCurrentScreen(s)}
              onRefresh={refreshAllData}
              onSelectProduct={(p) => setSelectedProductId(p.id)}
            />
          )}

          {currentScreen === 'product-detail' && (
            <ProductDetailView
              product={selectedProduct}
              onNavigate={(s) => setCurrentScreen(s)}
              onRefresh={refreshAllData}
              onSelectProduct={(p) => setSelectedProductId(p.id)}
            />
          )}

          {currentScreen === 'warranty' && (
            <WarrantyIntelligenceView
              products={products}
              selectedProduct={selectedProduct}
              onSelectProduct={(p) => setSelectedProductId(p.id)}
              onRefresh={refreshAllData}
            />
          )}

          {currentScreen === 'assistant' && (
            <AIAssistantView
              products={products}
              selectedProduct={selectedProduct}
              onSelectProduct={(p) => setSelectedProductId(p.id)}
              onNavigate={(s) => setCurrentScreen(s)}
              onRefresh={refreshAllData}
            />
          )}

          {currentScreen === 'service-requests' && (
            <ServiceRequestsView
              requests={requests}
              products={products}
              onRefresh={refreshAllData}
              onNavigate={(s) => setCurrentScreen(s)}
              statuses={statuses}
            />
          )}

          {currentScreen === 'recalls' && (
            <RecallsView
              recalls={recalls}
              products={products}
              onRefresh={refreshAllData}
            />
          )}

          {currentScreen === 'activity' && (
            <ActivityView
              activities={activities}
              onRefresh={refreshAllData}
              loading={loading}
            />
          )}

          {currentScreen === 'settings' && (
            <SettingsView
              keyStatus={keyStatus}
              onRefreshAll={refreshAllData}
              products={products}
            />
          )}
        </main>
      </div>
    </div>
  );
};

export default App;

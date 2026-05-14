import Image from "next/image";

import Header from "../components/header";
import Footer from "../components/footer";

export default function Home() {
  return (
    <div className="bg-white flex-1">
      <Header />

      <Footer />
    </div>
  );
}

import Image from "next/image";

import Header from "../components/header";
import Footer from "../components/footer";
import illustration from "../assets/images/Ilustration.png";
import moneyIcon from "../assets/money-icon.png";

const floatingIcons = [
  { top: "15%", left: "10%", size: 80 },
  { top: "5%", left: "40%", size: 80 },
  { top: "40%", left: "10%", size: 80 },
  { top: "50%", left: "43%", size: 80 },
  { top: "10%", left: "93.5%", size: 80 },
  { top: "65%", left: "93.5%", size: 80 },
  { top: "80%", left: "70%", size: 80 },
  { top: "80%", left: "35%", size: 80 },
  { top: "85%", left: "2%", size: 80 },
];

export default function Home() {
  return (
    <div className="bg-white min-h-screen flex flex-col">
      <Header />
      <main className="relative flex-1 overflow-hidden flex">
        {floatingIcons.map((icon, index) => (
          <div
            key={index}
            className="pointer-events-none absolute"
            style={{
              top: icon.top,
              left: icon.left,
              width: icon.size,
              height: icon.size,
            }}
          >
            <Image
              src={moneyIcon}
              alt="Floating money icon"
              fill
              sizes="80px"
              className="object-contain"
            />
          </div>
        ))}

        <div className="relative z-20 min-w-full min-h-full flex items-center ">
          <div className="pl-[22%]">
            <Image
              src={illustration}
              alt="Illustration"
              className="max-w-full h-auto"
              width={195}
            />
          </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
import Image from "next/image";

import Header from "../components/header";
import Footer from "../components/footer";
import illustration from "../assets/images/Ilustration.png";
import qrCode from "../assets/images/QR_Code.png";
import moneyIcon from "../assets/money-icon.png";

const floatingIcons = [
  { top: "15%", left: "10%"},
  { top: "5%", left: "40%"},
  { top: "40%", left: "10%"},
  { top: "50%", left: "43%"},
  { top: "10%", left: "93.5%"},
  { top: "65%", left: "93.5%"},
  { top: "80%", left: "70%"},
  { top: "80%", left: "35%"},
  { top: "85%", left: "2%"},
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
              width: 80,
              height: 80,
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

        <div className="relative z-20 min-w-full min-h-full flex flex-row items-center justify-between pr-[8%]">
          <div className="pl-[22%]">
            <Image
              src={illustration}
              alt="Illustration"
              className="max-w-full h-auto"
              width={195}
            />
          </div>
          <div className="w-100 py-4 px-6 flex flex-col rounded-3xl bg-[#76B74F]">
              <h3 className="text-2xl font-bold self-center">Consulte sua dívida agora!</h3>
              
              <div className="flex flex-col gap-2 pt-5 pb-8">
                <div className="flex flex-col gap-1">
                  <label className="text-inter text-[14px] font-semibold" htmlFor="">Documento</label>
                  <input type="text" className="h-10 border border-[#404040] bg-white text-[#6C757D] rounded-lg px-1.5" placeholder="Informe seu CPF ou CNPJ"/>
                </div>
              </div>
              
              <div className="flex flex-col gap-2">
                <button className="h-10 bg-[#1F6C74] font-inter font-bold text-[14px] text-white rounded-lg">Negociar dívida</button>
                <div className="flex flex-row items-center justify-center gap-2">
                  <div className="h-px bg-[#07513B] w-30"/>
                  <p>ou</p>
                  <div className="h-px bg-[#07513B] w-30"/>
                </div>
                <p className="text-[14px] text-center">acesse com o QR Code</p>
                <div className="self-center">
                  <Image 
                    src={qrCode}
                    alt="QR Code"
                    width={80}
                    height={80}
                  />
                </div>
              </div>
            </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}
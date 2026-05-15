import Image from "next/image";
import Link from "next/link";

import Header from "../../components/header";
import Footer from "../../components/footer";
import moneyIcon from "../../assets/money-icon.png";
import padlockIcon from "../../assets/icons/padlock.png";

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

export default function ForgotPassword() {
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

        <div className="relative z-20 min-w-full min-h-full flex flex-row items-center justify-center">
          <div className="w-100 py-4 px-6 flex flex-col rounded-3xl bg-[#76B74F]">
              <div className="w-30 h-30 mt-2.5 mb-5 self-center rounded-full bg-[#DAECCC] flex items-center justify-center">
                <Image 
                  src={padlockIcon}
                  alt="Padlock icon"
                  width={100}
                  height={100}
                />
              </div>
              <h3 className="text-2xl font-bold self-center">Esqueceu sua senha?</h3>
              <p className="text-center font-medium text-[14px] mt-4">
                Informe seu email para receber o<br />
                link de recuperação de senha
              </p>

              <div className="flex flex-col gap-2 pt-5 pb-10">
                <div className="flex flex-col gap-1">
                  <label className="text-inter text-[14px] font-semibold" htmlFor="">Email</label>
                  <input type="text" className="h-10 border border-[#404040] bg-white text-[#6C757D] rounded-lg px-1.5" placeholder="Digite seu email"/>
                </div>
              </div>
              
              <div className="flex flex-col gap-5 mb-5 items-center">
                <button className="h-10 w-full bg-[#1F6C74] font-inter font-bold text-[14px] text-white rounded-lg">
                  Enviar link de recuperação
                </button>

                <Link href="/login" className="text-sm underline text-[#07513B] cursor-pointer">Voltar a tela de login</Link>
              </div>
            </div>
        </div>
      </main>
      <Footer />
    </div>
  );
}